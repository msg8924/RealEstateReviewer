def filter_by_street(listings, street_names):
    if not street_names:
        return listings

    def match_street(address, streets):
        if not address:
            return False
        return any(street.lower() in address.lower() for street in streets)

    filtered = []
    for listing in listings:
        address = listing.get("address", "")
        if match_street(address, street_names):
            filtered.append(listing)

    print(f"🔍 Matched {len(filtered)} of {len(listings)} listings by street name")
    return filtered


def filter_listings_by_price(listings, price_min, price_max):
    filtered = []
    for listing in listings:
        price = listing.get("price")
        if price and price_min <= price <= price_max:
            filtered.append(listing)
    return filtered