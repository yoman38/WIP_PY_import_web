import requests
import pandas as pd
from io import StringIO
from datetime import datetime, timedelta
from typing import Dict

def etl_range_data(start_date: datetime, end_date: datetime):
    df_output = pd.DataFrame(
        columns=['UnitDate', 'Data', 'Godzina', 'CRO', 'CROs', 'CROz', 'Stan zakontraktowania', 'Niezbilansowanie'])

    current_date = start_date
    while current_date <= end_date:
        df_date = get_data(current_date)
        df_output = pd.concat([df_output, df_date], ignore_index=True)
        current_date += timedelta(days=1)
    return df_output  # Return the final dataframe


def get_data(date: datetime) -> pd.DataFrame:
    df_output = pd.DataFrame()

    range_dates = convert_to_range_dates(date)
    url = f"https://www.pse.pl/getcsv/-/export/csv/PL_CENY_NIEZB_RB/data_od/{range_dates['start_date_str']}/data_do/{range_dates['end_date_str']}"
    print(url)

    try:
        response = requests.get(url, timeout=180)
        csv_data = response.text
        df_csv = pd.read_csv(StringIO(csv_data), sep=';')
        df_csv.loc[:, 'UnitDate'] = date.date()
        df_csv = df_csv[df_csv["Data"].astype(str) == range_dates['start_date_str']] # Make sure to convert both sides to string for comparison

        df_output = pd.concat([df_output, df_csv], ignore_index=True)

        # Convert data types
        columns_to_convert = ['CRO', 'CROs', 'CROz', 'Stan zakontraktowania', 'Niezbilansowanie']

        for column in columns_to_convert:
            df_output[column] = df_output[column].apply(lambda x: x.replace(',', '.') if x != '-' else None)
            df_output[column] = pd.to_numeric(df_output[column], errors='coerce')

        # Rename headers
        df_output = df_output.rename(columns={'Godzina': 'Hour',
                                              'Stan zakontraktowania': 'ContractingStatusValue',
                                              'Niezbilansowanie': 'ImbalanceValue'})
        return df_output
    except Exception as e:
        print(f"Error: {str(e)}")
        return df_output
