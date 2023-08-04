import sys
from datetime import datetime, timedelta
import dwh_service
import rdn_ee_indices
import rdn_gas_index


def main():
    current_date = datetime.now()
    download_date = current_date - timedelta(days=1)

    # RDN: Pobranie indeksów EE
    df_ee_indices = rdn_ee_indices.get_indices_data(download_date)

    if df_ee_indices is None:
        sys.exit(1)

    delivery_date = df_ee_indices['DeliveryDate'][0]
    dwh_service.delete_from_sql(rdn_ee_indices.DESTINATION_TABLE_NAME, delivery_date)
    dwh_service.add_data_to_sql(rdn_ee_indices.DESTINATION_TABLE_NAME, df_ee_indices)

    # RDN: Pobranie indeksu Gaz
    df_gas_index = rdn_gas_index.get_gas_index(download_date)

    if df_gas_index is None:
        sys.exit(1)

    gas_delivery_date = df_gas_index['DeliveryDate'][0]
    dwh_service.delete_from_sql(rdn_gas_index.DESTINATION_TABLE_NAME, gas_delivery_date)
    dwh_service.add_data_to_sql(rdn_gas_index.DESTINATION_TABLE_NAME, df_gas_index)


if __name__ == '__main__':
    main()
