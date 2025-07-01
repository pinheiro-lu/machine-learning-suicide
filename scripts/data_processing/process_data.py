from src.data_processing import merge_wdi_who_data

if __name__ == "__main__":
    merge_wdi_who_data(
        wdi_path='data/raw/wdi_data.csv',
        who_path='data/raw/who_data.csv',
        civ_prk_path='data/raw/wdi_civ_prk_data.csv',
        output_path='data/processed/merged_data.csv'
    )
