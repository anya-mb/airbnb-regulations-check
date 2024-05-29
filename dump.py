import os
from dotenv import load_dotenv
import requests
import time
import csv

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv('RAPIDAPI_KEY')

# Constants
API_HOST = "airbnb13.p.rapidapi.com"
BASE_URL = "https://airbnb13.p.rapidapi.com/search-geo"
HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST,
    "Content-Type": "application/json"
}

QUERYSTRING = {
    "location": "Vancouver, BC, Canada",
    "checkin": "2024-07-01", # change for different dump
    "checkout": "2024-07-04", # change for different dump
    "adults": "1",
    "children": "0",
    "infants": "0",
    "pets": "0",
    "page": "1",
    "currency": "CAD"
}

DATA_FILENAME = f'data/airbnb_results_{QUERYSTRING["checkin"]}_{QUERYSTRING["checkout"]}.csv'


# Function to make the API request
def make_request(page):
    QUERYSTRING['page'] = page
    response = requests.get(BASE_URL, headers=HEADERS, params=QUERYSTRING)
    response.raise_for_status()  # Check for request errors
    return response.json()


# Function to extract and flatten the relevant data
def extract_data(result):
    try:
        return {
            'id': result.get('id', ''),
            'userId': result.get('userId', ''),
            'name': result.get('name', ''),
            'address': result.get('address', ''),
            'city': result.get('city', ''),
            'isSuperhost': result.get('isSuperhost', False),
            'lat': result.get('lat', ''),
            'lng': result.get('lng', ''),
            'persons': result.get('persons', 0),
            'rating': result.get('rating', 0.0),
            'reviewsCount': result.get('reviewsCount', 0),
            'type': result.get('type', ''),
            'cancelPolicy': result.get('cancelPolicy', ''),
            'deeplink': result.get('deeplink', ''),
            'hostThumbnail': result.get('hostThumbnail', ''),
            'price_currency': result['price'].get('currency', ''),
            'price_rate': result['price'].get('rate', 0),
            'price_total': result['price'].get('total', 0),
            'bathrooms': result.get('bathrooms', 0),
            'bedrooms': result.get('bedrooms', 0),
            'beds': result.get('beds', 0),
            'previewAmenities': ', '.join(result.get('previewAmenities', [])),
            'url': result.get('url', ''),
            'images': result.get('images', []),
            'amenityIds': result.get('amenityIds', [])
        }
    except KeyError as e:
        print(f"Missing key in result: {e}")
        print("Result data:", result)
        return {}


# Main script
def main():
    seen_ids = set()
    page = 1
    is_first_write = True

    while True:
        print(f"Fetching page {page}...")
        data = make_request(page)
        results = data.get('results', [])
        if not results:
            break

        # Check for duplicates
        new_results = []
        for result in results:
            listing_id = result['id']
            if listing_id not in seen_ids:
                seen_ids.add(listing_id)
                new_results.append(result)

        if not new_results:
            print("Duplicate results detected. Stopping.")
            break

        # Save the results to a CSV file incrementally
        with open(DATA_FILENAME, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'id', 'userId', 'name', 'address', 'city', 'isSuperhost', 'lat', 'lng', 'persons',
                'rating', 'reviewsCount', 'type', 'cancelPolicy', 'deeplink', 'hostThumbnail',
                'price_currency', 'price_rate', 'price_total', 'bathrooms', 'bedrooms',
                'beds', 'previewAmenities', 'url', 'images', 'amenityIds'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if is_first_write:
                writer.writeheader()
                is_first_write = False
            for result in new_results:
                data = extract_data(result)
                if data:
                    writer.writerow(data)

        page += 1
        time.sleep(61)  # Ensure no more than 1 request per minute

    print("Data collection completed.")


if __name__ == "__main__":
    main()
