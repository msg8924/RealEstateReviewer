import requests
import csv
import yaml
import datetime
from utils import filter_by_street, filter_listings_by_price


def load_config(path="config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def search_all_locations(config):
    results = []
    headers = {
        "X-RapidAPI-Key": config["api_key"],
        "X-RapidAPI-Host": config["api_host"]
    }

    locations = config["search"].get("locations", [])
    zip_codes = config["search"].get("zip_codes", [])
    home_types = config["search"].get("home_types", ["SINGLE_FAMILY"])
    search_targets = locations + zip_codes

    for location in search_targets:
        for home_type in home_types:
            params = {
                "location": location,
                "home_type": home_type,
                "status_type": config["search"].get("status_type", "ForSale"),
                "price_min": config["search"].get("price_min"),
                "price_max": config["search"].get("price_max"),
                "beds_min": config["search"].get("beds_min"),
                "baths_min": config["search"].get("baths_min")
            }

            print(f"🔎 Searching {location} | Type: {home_type} | Filters: {params}")
            try:
                response = requests.get(config["api_url"], headers=headers, params=params)
                response.raise_for_status()
                listings = response.json().get("props", [])
                print(f"✅ Found {len(listings)} listings in {location} ({home_type})")
                results.extend(listings[:config["search"].get("limit", 50)])
            except Exception as e:
                print(f"❌ Error fetching {location} ({home_type}): {e}")

    return results

def convert_timestamp(value):
    if isinstance(value, (int, float)) and 1e12 < value < 2e12:
        try:
            return datetime.datetime.fromtimestamp(value / 1000).strftime("%Y-%m-%d")
        except:
            return value
    return value

def save_to_csv(listings, filename="raw_results.csv"):
    if not listings:
        print("No listings to save.")
        return

    # Determine all unique keys
    all_keys = set()
    for listing in listings:
        all_keys.update(listing.keys())
    all_keys = sorted(all_keys)

    # Add address components to the header
    fieldnames = ['street', 'city', 'state', 'zipcode'] + all_keys

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for listing in listings:
            row = {key: convert_timestamp(listing.get(key, "")) for key in all_keys}
            # Parse the address into components
            full_address = listing.get("address", "")
            street, city, state, zipcode = "", "", "", ""
            if full_address:
                parts = [part.strip() for part in full_address.split(',')]
                if len(parts) == 3:
                    street = parts[0]
                    city = parts[1]
                    state_zip = parts[2].split()
                    if len(state_zip) == 2:
                        state, zipcode = state_zip
            row.update({
                'street': street,
                'city': city,
                'state': state,
                'zipcode': zipcode
            })
            writer.writerow(row)

    print(f"📄 Saved {len(listings)} full listings to {filename}")

def main():
    config = load_config()
    all_listings = search_all_locations(config)
    price_min = config["search"].get("price_min", 0)
    price_max = config["search"].get("price_max", float("inf"))
    street_names = config["search"].get("street_names", [])

    filtered_by_price = filter_listings_by_price(all_listings, price_min, price_max)
    filtered_by_street = filter_by_street(filtered_by_price, street_names)

    save_to_csv(filtered_by_street)  # Full raw output

if __name__ == "__main__":
    main()
