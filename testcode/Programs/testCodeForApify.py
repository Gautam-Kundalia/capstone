from apify_client import ApifyClient
import csv
import json

# Initialize the Apify client with your API token
apify_client = ApifyClient('apify_api_EeQGgLRxLQWhXcKZnJCNRiQdHCHELC11ZW1v')

# Define the input for the actor
input_data = {
    "startUrls": [
        {"url": "https://www.behavioralcrossroads.com/alcohol-misuse-prevention/"}
    ]
}

# # Start the Actor with the input data and wait for it to finish
# actor_call = apify_client.actor('apify/website-content-crawler').call(run_input=input_data)

# Fetch results from the Actor run's default dataset
dataset_items = apify_client.dataset('fKQeG1TSQmzsDYmQg').list_items().items

# Print the fetched results
print(dataset_items)
