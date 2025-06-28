import json

def analyze_json(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            print(f"Total records: {len(data)}")
            
            missing_values = [record for record in data if 'value' not in record or record['value'] is None]
            print(f"Records with missing 'value': {len(missing_values)}")
            
            if missing_values:
                print("Sample missing records:")
                for record in missing_values[:5]:  # Show a few examples
                    print(record)
    except Exception as e:
        print(f"Error reading JSON file: {e}")

# Analyze the temp_data.json file
analyze_json('datasets/temp_data.json')