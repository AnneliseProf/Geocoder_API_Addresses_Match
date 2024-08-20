import pandas as pd
import requests
import csv
import time
import json

def geocode_address(address):
    url = 'https://geocoding.geo.census.gov/geocoder/geographies/address'
    params = {
        'street': address[1],
        'city': address[2],
        'state': address[3],
        'zip': address[4],
        'benchmark': 'Public_AR_Current',
        'vintage': 'Current_Current',
        'format': 'json'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        raw_response = json.dumps(data, indent=2)  # Store the raw JSON response
        
        if data['result']['addressMatches']:
            match = data['result']['addressMatches'][0]
            geographies = match.get('geographies', {})
            census_tracts =  geographies.get('Census Tracts', [{}])[0]
            census_blocks = geographies.get('2020 Census Blocks', [{}])[0]
            return {
                'id': address[0],
                'input_address': f"{address[1]}, {address[2]}, {address[3]} {address[4]}",
                'match_indicator': 'Match',
                'matched_address': match['matchedAddress'],
                'longitude': match['coordinates']['x'],
                'latitude': match['coordinates']['y'],
                'tigerline_id': match['tigerLine']['tigerLineId'],
                'side': match['tigerLine']['side'],
                'state_fips': census_tracts.get('STATE', ''),
                'county_fips': census_tracts.get('COUNTY', ''),
                'tract': census_tracts.get('TRACT', ''),
                'block': census_blocks.get('BLOCK', ''),
                'raw_response': raw_response,  # Include the raw JSON response
                'beautified_response': json.dumps(data, indent=4, sort_keys=True)  # Beautified JSON
            }
    return {
        'id': address[0],
        'input_address': f"{address[1]}, {address[2]}, {address[3]} {address[4]}",
        'match_indicator': 'No_Match',
        'matched_address': '',
        'longitude': '',
        'latitude': '',
        'tigerline_id': '',
        'side': '',
        'state_fips': '',
        'county_fips': '',
        'tract': '',
        'block': '',
        'raw_response': '',  # Empty string for raw response in case of no match
        'beautified_response': ''  # Empty string for beautified response in case of no match
    }

# Read the input CSV file
input_file = 'Addresses.csv'
addresses = []

with open(input_file, 'r') as infile:
    csv_reader = csv.reader(infile)
    next(csv_reader)  # Skip the header row
    for row in csv_reader:
        addresses.append(row)

# Process each address
results = []
for address in addresses:
    print(f"Processing: {address[1]}, {address[2]}, {address[3]} {address[4]}")
    result = geocode_address(address)
    results.append(result)
    time.sleep(0.1)  # Add a small delay to avoid overwhelming the API

# Create a DataFrame from the results
df = pd.DataFrame(results)

# Display results
with pd.option_context(
    'display.width', None,
    'display.max_columns', None,
    'display.max_colwidth', None,
    'display.colheader_justify', 'left'):
    print("Full results:")


# Save results to CSV
df.to_csv('geocoded_results_detailed.csv', index=False)
print("\nFull results saved to 'geocoded_results_detailed.csv'")
