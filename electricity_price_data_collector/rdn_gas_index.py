import dataclasses

import pandas as pd
import requests
import re
from typing import Dict, Optional
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# https://tge.pl/gaz-rdn?dateShow=27-04-2023&dateAction=
DESTINATION_TABLE_NAME = 'TestEnv_TGE_RDN_Gas_StockIndices'
HTML_SOURCE_TABLE_NAME = 'footable_indeksy_0'
TARGET_INDEX_NAME = 'TGEgasDA'


def get_gas_index(download_date) -> Optional[pd.DataFrame]:
    try:
        date_string = download_date.strftime('%d-%m-%Y')
        url = f'https://tge.pl/gaz-rdn?dateShow={date_string}&dateAction='
        response = requests.get(url)
        response.raise_for_status()  # Podnosi wyjątek dla kodu odpowiedzi różnego od 200, alt dla if == 200

        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        # DeliveryDate - data dostawy => data notowania + 1
        section = soup.find('section',
                            {'class': 'mainContainer padding-bottom-20 padding-top-20 bg_lightLightGreen'})
        header = section.find('h4')
        delivery_date_str = re.search(r"\d{2}-\d{2}-\d{4}", header.text).group(0)
        delivery_date = datetime.strptime(delivery_date_str, '%d-%m-%Y')  # 25-05-2023
        delivery_date = delivery_date.strftime('%Y-%m-%d %H:%M:%S.%f')  # 2023-05-25 dla porownania z unit_date

        unit_date = download_date.strftime('%Y-%m-%d %H:%M:%S.%f')

        # GUARD
        if delivery_date == unit_date:
            return None

        df = get_data(soup)

        df['UnitDate'] = unit_date
        df['DeliveryDate'] = delivery_date

        return df

    except requests.exceptions.RequestException as ex:
        # Logger
        print(ex)
        return None


def get_data(soup) -> Optional[pd.DataFrame]:
    try:
        # Table Content
        df_output = pd.DataFrame(columns=['UnitDate', 'Name', 'Value', 'Volume'])
        table = soup.find('table', id=HTML_SOURCE_TABLE_NAME)
        if table:
            df_table_content = extract_html_table(table)
            df_output = pd.concat([df_output, df_table_content], ignore_index=True)

        return df_output
    except requests.exceptions.RequestException as ex:
        # Logger
        print(ex)
        return None


def extract_html_table(table) -> pd.DataFrame:
    df_output = pd.DataFrame(columns=['UnitDate', 'Name', 'Value', 'Volume'])

    rows = table.find_all('tr')
    # Wiersz 0 Nagłówek
    # Wiersz 1 teoretyczna pozycja TGEgasDA
    for i in range(1, 3):
        row_index = i
        cells = rows[row_index].find_all('td')

        contract_name = cells[0].text
        if contract_name != TARGET_INDEX_NAME:
            continue

        value = re.sub(r'[^\d.,-]', '', cells[2].text)  # Kurs [PlN/MWh]
        volume = re.sub(r'[^\d.,-]', '', cells[4].text)  # Wolumen [MWh]

        if value == '-' or value == '':
            value_float = None
        else:
            value_float = float(value.replace(',', '.'))

        if volume == '-' or volume == '':
            volume_float = None
        else:
            volume_float = float(volume.replace(',', '.'))

        hc_data = {'Name': contract_name, 'Value': value_float, 'Volume': volume_float}
        df_q_content = pd.DataFrame([hc_data])
        df_output = pd.concat([df_output, df_q_content], ignore_index=True)

    return df_output
