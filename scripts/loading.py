from src.data_processing import merge_wdi_who_data

if __name__ == "__main__":
    merge_wdi_who_data(
        wdi_path='datasets/wdi_data.csv',
        who_path='datasets/who_data.csv',
        civ_prk_path='datasets/wdi_civ_prk_data.csv',
        output_path='datasets/merged_data.csv'
    )