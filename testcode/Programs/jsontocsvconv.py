from apify_client import ApifyClient
import csv

def flatten_json(json_obj, parent_key='', sep='_'):
    """
    Recursively flatten a nested JSON object into a single-level dictionary.
    Keys from nested objects will be joined with the separator (default '_').
    """
    flattened = {}
    for key, value in json_obj.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            # Recursively flatten nested dictionaries
            flattened.update(flatten_json(value, new_key, sep=sep))
        else:
            # Add simple key-value pair
            flattened[new_key] = value
    return flattened

# Initialize the Apify client with your API token
apify_client = ApifyClient('apify_api_EeQGgLRxLQWhXcKZnJCNRiQdHCHELC11ZW1v')

# Define the input for the actor (if required to run the actor again)
input_data = {
    "startUrls": [
        {"url": "https://www.behavioralcrossroads.com/alcohol-misuse-prevention/"}
    ]
}

# Fetch results from the Actor run's default dataset
dataset_items = apify_client.dataset('fKQeG1TSQmzsDYmQg').list_items().items

# Flatten all JSON objects in the dataset
flattened_items = [flatten_json(item) for item in dataset_items]

# Extract the CSV headers (all unique keys across all JSON objects)
headers = set()
for item in flattened_items:
    headers.update(item.keys())
headers = sorted(headers)  # Optional: Sort headers alphabetically

# Write the flattened JSON data to a CSV file
output_file = 'output.csv'
with open(output_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()  # Write the headers
    writer.writerows(flattened_items)  # Write the rows

print(f"Data has been written to {output_file}")
