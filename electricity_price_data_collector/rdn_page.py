from dataclasses import dataclass
from typing import List


@dataclass
class RdnPageConfig:
    # Indeksy
    stock_indices_html_tables = ['footable_indeksy_0', 'footable_indeksy_1']
    stock_indices_table_row_id = 1
    stock_index_name_cell_id: int = 0
    stock_index_value_cell_id: int = 2
    stock_index_volume_cell_id: int = 4

    # Kontrakty godzinowe
    hc_delivery_date_h4_class_name = 'kontrakt-date'  # matka: 'section' class='mainContainer padding-top-30'
    hc_html_table_id = 'footable_kontrakty_godzinowe' # matka: section nizej div class table-responsive wyniki-table-kontrakty-godzinowe

    hc_q_types = {1: 'Fixing1', 3: 'Fixing2',  5: 'NotowaniaCiagle'}
    hc_hour_cell_id = 0

    hc_fixing_1_value_cell_id = 1
    hc_fixing_1_volume_cell_id = 2

    hc_fixing_2_value_cell_id = 3
    hc_fixing_2_volume_cell_id = 4

    hc_continuous_value_cell_id = 5
    hc_continuous_volume_cell_id = 6
