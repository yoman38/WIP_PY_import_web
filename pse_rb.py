import requests
import pandas as pd
from io import StringIO
from datetime import datetime, timedelta
from typing import Dict
import dwh_service

DESTINATION_TABLE_NAME = 'PSE_RB_PricesAndImbalances_LT'


def etl_range_data(start_date: datetime, end_date: datetime):
    # df_output = pd.DataFrame(
    #     columns=['UnitDate', 'Data', 'Hour', 'CRO', 'CROs', 'CROz', 'ContractingStatusValue', 'ImbalanceValue'])

    current_date = start_date
    while current_date <= end_date:
        df_date = get_data(current_date)
        # df_output = pd.concat([df_output, df_date], ignore_index=True)

        if df_date is not None:
            dwh_service.add_data_to_sql(DESTINATION_TABLE_NAME, df_date)

        current_date += timedelta(days=1)


def get_data(date: datetime) -> pd.DataFrame:
    df_output = pd.DataFrame(
        columns=['UnitDate', 'Data', 'Godzina', 'CRO', 'CROs', 'CROz', 'Stan zakontraktowania', 'Niezbilansowanie'])

    range_dates = convert_to_range_dates(date)
    url = f"https://www.pse.pl/getcsv/-/export/csv/PL_CENY_NIEZB_RB/data_od/{range_dates['start_date_str']}/data_do/{range_dates['end_date_str']}"
    print(url)

    try:
        response = requests.get(url, timeout=180)

        csv_data = response.text
        df_csv = pd.read_csv(StringIO(csv_data), sep=';')
        df_csv.loc[:, 'UnitDate'] = date.date()
        df_csv = df_csv.query(f"Data == {range_dates['start_date_str']}")

        df_output = pd.concat([df_output, df_csv], ignore_index=True)
        print(df_csv.size)

        # Konwertowanie
        columns_to_convert = ['CRO', 'CROs', 'CROz', 'Stan zakontraktowania', 'Niezbilansowanie']

        for column in columns_to_convert:
            df_output[column] = df_output[column].apply(lambda x: x.replace(',', '.') if x != '-' else None)
            pd.to_numeric(df_output[column], errors='coerce')

        # Zmiana nazw nagłówków
        df_output = df_output.rename(columns={'Godzina': 'Hour',
                                              'Stan zakontraktowania': 'ContractingStatusValue',
                                              'Niezbilansowanie': 'ImbalanceValue'})
        return df_output
    except:
        print('Error')


def convert_to_range_dates(date: datetime) -> Dict:
    start_date = date.strftime('%Y%m%d')
    end_date = date + timedelta(days=1)
    end_date = end_date.strftime('%Y%m%d')
    return {'start_date_str': start_date, 'end_date_str': end_date}
