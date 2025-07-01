import pandas as pd
import requests

def fetch_wdi_country_classifications(save_path='data/raw/wdi_country_classifications.csv'):
    # World Bank API for country metadata
    url = 'http://api.worldbank.org/v2/country?per_page=400&format=json'
    r = requests.get(url)
    data = r.json()[1]
    records = []
    for entry in data:
        records.append({
            'iso3': entry['id'],
            'name': entry['name'],
            'region': entry['region']['value'],
            'income_group': entry['incomeLevel']['value'],
            'lending_type': entry['lendingType']['value']
        })
    df = pd.DataFrame(records)
    df.to_csv(save_path, index=False)
    print(f"Saved country classifications to {save_path}")

if __name__ == '__main__':
    fetch_wdi_country_classifications()
