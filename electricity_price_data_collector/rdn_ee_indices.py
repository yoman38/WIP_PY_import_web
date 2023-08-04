import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
from typing import Dict, Optional
from datetime import datetime, timedelta
import dwh_service
from rdn_page import RdnPageConfig


DESTINATION_TABLE_NAME = "TestEnv_TGE_RDN_StockIndices"


def download_rdn_history_data(table_name: str):
    df_output = pd.DataFrame(columns=['StockIndex', 'UnitDate', 'Value', 'Volume', 'DeliveryDate'])
    start_date = datetime(2023, 6, 23)
    end_date = datetime.now()
    current_date = start_date
    while current_date <= end_date:
        # Logika
        data_by_day = get_indices_data(current_date)

        if data_by_day is not None:
            df_output = pd.concat([df_output, data_by_day], ignore_index=False)

        current_date += timedelta(days=1)

    dwh_service.add_data_to_sql(table_name, df_output)


def get_indices_data(date) -> Optional[pd.DataFrame]:
    rdn_page_config = RdnPageConfig()
    try:
        date_string = date.strftime('%d-%m-%Y')
        url = f'https://tge.pl/energia-elektryczna-rdn?dateShow={date_string}&dateAction=next'
        response = requests.get(url)
        response.raise_for_status()  # Podnosi wyjątek dla kodu odpowiedzi różnego od 200, alt dla if == 200

        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        # Sprawdzenie daty notowan => gdy dla data z url nie ma notowan, to wyswietlana jest ostatnia znana
        # Decyduje data z inputu id = 'datepicker', jednakze nie mozna go namierzyc. Chyba DI z js.

        # UnitDate - data notowania
        unit_date = date.strftime('%Y-%m-%d %H:%M:%S.%f')

        # DeliveryDate - data dostawy => data notowania + 1
        section = soup.find('section',
                            {'class': 'mainContainer padding-bottom-20 padding-top-20 bg_lightLightGreen'})
        header = section.find('h4')
        delivery_date_str = re.search(r"\d{2}-\d{2}-\d{4}", header.text).group(0)
        delivery_date = datetime.strptime(delivery_date_str, '%d-%m-%Y')  # 25-05-2023
        delivery_date = delivery_date.strftime('%Y-%m-%d %H:%M:%S.%f')  # 2023-05-25 dla porownania z unit_date

        # GUARD
        if delivery_date == unit_date:
            return None

        # Table Content
        df_output = pd.DataFrame(columns=['StockIndex', 'UnitDate', 'Value', 'Volume', 'DeliveryDate'])
        for table_id in rdn_page_config.stock_indices_html_tables:  # ['footable_indeksy_0', 'footable_indeksy_1']
            table = soup.find('table', id=table_id)
            if table:
                dict_table_content = extract_data_from_html_table(table)
                df_table_content = pd.DataFrame([dict_table_content])
                df_output = pd.concat([df_output, df_table_content], ignore_index=True)

        df_output['UnitDate'] = unit_date
        df_output['DeliveryDate'] = delivery_date

        return df_output
    except requests.exceptions.RequestException as ex:
        # Logger
        print(ex)
        return None


def extract_data_from_html_table(table) -> Dict[str, float]:
    rdn_page_config = RdnPageConfig()
    row_index = rdn_page_config.stock_indices_table_row_id
    max_column_index = rdn_page_config.stock_index_volume_cell_id

    rows = table.find_all('tr')
    if len(rows) > row_index:
        cells = rows[row_index].find_all('td')
        if len(cells) > max_column_index:
            stock_index = cells[rdn_page_config.stock_index_name_cell_id].text  # TGeBas
            value = cells[rdn_page_config.stock_index_value_cell_id].text  # Kurs [PlN/MWh]
            volume = cells[rdn_page_config.stock_index_volume_cell_id].text  # Wolumen [MWh]

            value_float = float(value.replace(',', '.'))
            volume_float = float(volume.replace(',', '.'))

            table_content = {'StockIndex': stock_index, 'Value': value_float, 'Volume': volume_float}
            return table_content


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
