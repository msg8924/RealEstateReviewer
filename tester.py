import requests

url = "https://zillow-com1.p.rapidapi.com/propertyExtendedSearch"

querystring = {
    "location": "Los Angeles, CA",
    "status_type": "ForSale",
    "home_type": "Houses"
}

headers = {
    "X-RapidAPI-Key": "0e5355b710msh91ba008289b7be7p10db3bjsnb4e9987d2a8d",
    "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print("Status Code:", response.status_code)

if response.status_code == 200:
    data = response.json()
    results = data.get("props", [])
    print(f"✅ Found {len(results)} listings")
    for listing in results[:10]:
        print(f"{listing.get('address')} - ${listing.get('price')}")
else:
    print("❌ API Error:", response.text)
