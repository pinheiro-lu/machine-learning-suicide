import pandas as pd
import wbdata

wdi_data = pd.read_csv('datasets/wdi_data.csv')

# Print unique series names from the WDI dataset
unique_series_names = wdi_data['Series Name'].unique()
print("Unique series names in WDI data:", unique_series_names)

