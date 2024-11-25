# Installing Libraries
import pandas as pd
import os
import requests
from django.conf import settings
from django.templatetags.static import static  # Utility to resolve static file paths
import csv
import re
import requests
from geopy.geocoders import Nominatim
import geocoder

# API Configurations
UPCITEMDB_API_URL = 'https://api.upcitemdb.com/prod/trial/search'
OPENFOODFACTS_API_URL = 'https://world.openfoodfacts.org/api/v0/product/'
GOOGLE_API_KEY = settings.GOOGLE_API_KEY  # Replace with your Google API key
# API Key for Yelp
YELP_API_KEY = settings.YELP_API_KEY
OPENCAGE_API_KEY = settings.OPENCAGE_API_KEY
BARCODE_LOOKUP_API_KEY = settings.BARCODE_LOOKUP_API

headers = {
    'Authorization': f'Bearer {YELP_API_KEY}',
}

YELP_URL = 'https://api.yelp.com/v3/businesses/search'

# Defining a function to get coordinates based on address
def get_coordinates(address):
    """
    Retrieves the GPS coordinates for a given address using the OpenCage Geocoding API.
    """
    url = f'https://api.opencagedata.com/geocode/v1/json?q={address}&key={OPENCAGE_API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            location = data['results'][0]['geometry']
            return location['lat'], location['lng']
        else:
            print('No results found for the given address.')
    else:
        print(f'Error: {response.status_code}')
    return None, None

# Defining a function to get nutrition info from Open Food Facts
def get_open_food_facts_info_by_name(grocery_name):
    # Declaring variables
    produce_items = []
    produce_name = grocery_name

    # Fetch product data from Open Food Facts API using search endpoint
    url = f'https://world.openfoodfacts.org/cgi/search.pl'
    params = {
        'search_terms': produce_name,
        'search_simple': 1,
        'json': 1
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        products = data.get('products', [])
        
        if products:  # Products found
            for product in products[:5]:  # Limiting to the first 5 results
                nutriments = product.get('nutriments', {})
                
                # Extract product details
                produce_items.append({
                    'produce_name': produce_name,
                    'product_name': product.get('product_name', 'N/A'),
                    'plu_code': product.get('code', 'N/A'),  # Extract PLU code
                    'brand': product.get('brands', 'N/A'),
                    'categories': product.get('categories', 'N/A'),
                    'labels': product.get('labels', 'N/A'),
                    'packaging': product.get('packaging', 'N/A'),
                    'ingredients': product.get('ingredients_text', 'N/A'),
                    'allergens': product.get('allergens_tags', 'N/A'),
                    'additives': product.get('additives_tags', 'N/A'),
                    'serving_size': product.get('serving_size', 'N/A'),
                    'serving_quantity': product.get('serving_quantity', 'N/A'),
                    'nutrition_grade': product.get('nutrition_grades', 'N/A'),
                    'image_url': product.get('image_url', ''),
                    'calories': nutriments.get('energy-kcal_100g', 'N/A'),
                    'fat': nutriments.get('fat_100g', 'N/A'),
                    'saturated_fat': nutriments.get('saturated-fat_100g', 'N/A'),
                    'carbohydrates': nutriments.get('carbohydrates_100g', 'N/A'),
                    'sugars': nutriments.get('sugars_100g', 'N/A'),
                    'fiber': nutriments.get('fiber_100g', 'N/A'),
                    'proteins': nutriments.get('proteins_100g', 'N/A'),
                    'salt': nutriments.get('salt_100g', 'N/A'),
                    'sodium': nutriments.get('sodium_100g', 'N/A'),
                    'origins': product.get('origins', 'N/A'),
                    'manufacturing_places': product.get('manufacturing_places_tags', 'N/A'),
                    'ecoscore_grade': product.get('ecoscore_grade', 'N/A'),
                    'stores': product.get('stores', 'N/A'),
                    'product_url': product.get('url', 'N/A')
                })
        else:
            # No products found
            produce_items.append({
                'produce_name': produce_name,
                'product_name': 'N/A',
                'plu_code': 'N/A',
                'brand': 'N/A',
                'categories': 'N/A',
                'labels': 'N/A',
                'packaging': 'N/A',
                'ingredients': 'N/A',
                'allergens': 'N/A',
                'additives': 'N/A',
                'serving_size': 'N/A',
                'serving_quantity': 'N/A',
                'nutrition_grade': 'N/A',
                'image_url': '',
                'calories': 'N/A',
                'fat': 'N/A',
                'saturated_fat': 'N/A',
                'carbohydrates': 'N/A',
                'sugars': 'N/A',
                'fiber': 'N/A',
                'proteins': 'N/A',
                'salt': 'N/A',
                'sodium': 'N/A',
                'origins': 'N/A',
                'manufacturing_places': 'N/A',
                'ecoscore_grade': 'N/A',
                'stores': 'N/A',
                'product_url': 'N/A'
            })
    else:
        print(f"Error fetching data: {response.status_code}")
    
    return produce_items


# Defining a function to lookup avg prices based on barcode
def get_prices_and_average(barcode):
    # API key for Barcode Lookup
    url = f"https://api.barcodelookup.com/v3/products"

    # Parameters for the API call
    params = {
        "barcode": barcode,
        "key": BARCODE_LOOKUP_API_KEY
    }

    # Make the GET request
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        products = data.get("products", [])
        if products:
            product = products[0]  # Get the first product
            stores = product.get("stores", [])
            #getting size
            size = product.get("size", "N/A")

            # Extract prices from stores
            prices = [
                float(store.get("price").replace("$", "").strip()) 
                for store in stores if store.get("price")
            ]

            if prices:
                average_price = sum(prices) / len(prices)
                #getting the lowest price
                lowest_price = min(prices)
                return {"prices": prices, "average_price": round(average_price, 2), "minimum_price": round(lowest_price, 2), 'sizes': size}
            else:
                return {"error": "No price information available for this product."}
        else:
            return {"error": "Product not found."}
    else:
        return {"error": f"Error: Unable to fetch data. Status code: {response.status_code}"}


# Defining a function to get google maps link based on user address
def get_google_maps_link(address):
    """Generate a Google Maps link for a given address."""
    base_url = "https://www.google.com/maps/search/?api=1&query="
    formatted_address = address.replace(" ", "+")
    return base_url + formatted_address


# Defining a function to organise store hours
def format_business_hours(business_hours):
    """Converts the business hours data into a more readable dictionary format.

    Args:
        business_hours (dict): The business hours data from the Yelp API.

    Returns:
        dict: A dictionary representing the business hours in a readable format,
              or an empty dictionary if the input is invalid.
    """
    formatted_hours = {}
    if not business_hours or not isinstance(business_hours, list) or not business_hours[0].get('open'):
        return formatted_hours  # Return an empty dict for invalid input

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for hour_entry in business_hours[0]['open']:
        day_index = hour_entry['day']
        start_time = hour_entry['start']
        end_time = hour_entry['end']

        # Format time in 12-hour format
        start_hour = int(start_time[:2])
        start_minute = start_time[2:]
        start_am_pm = "AM" if start_hour < 12 else "PM"
        start_hour = start_hour % 12
        if start_hour == 0:
          start_hour = 12
        
        end_hour = int(end_time[:2])
        end_minute = end_time[2:]
        end_am_pm = "AM" if end_hour < 12 else "PM"
        end_hour = end_hour % 12
        if end_hour == 0:
          end_hour = 12
        
        formatted_start_time = f"{start_hour}:{start_minute} {start_am_pm}"
        formatted_end_time = f"{end_hour}:{end_minute} {end_am_pm}"
        
        formatted_hours[days[day_index]] = f"{formatted_start_time} - {formatted_end_time}"

    return formatted_hours


# Write a function to get store information based on inputed address
def find_nearby_grocery_stores_by_address(radius, categories, open_now, address):
    store_data = []
    
    # Get latitude and longitude
    latitude, longitude = get_coordinates(address)
    params = {
        'categories': categories,
        'open_now': open_now,
        'latitude': latitude,
        'longitude': longitude,
        'radius': radius,
        'limit': 5,  # Limit to 5 results for simplicity
    }

    # Make the API request
    response = requests.get(YELP_URL, headers=headers, params=params)
    data = response.json()

    # Check if businesses were found
    if data.get('businesses'):
        sorted_businesses = sorted(data['businesses'], key=lambda x: x['distance'])
        
        for business in sorted_businesses:
            name = business.get('name', 'N/A')
            address = ', '.join(business['location'].get('display_address', []))
            store_coordinates = business.get('coordinates', {})
            latitude = store_coordinates.get('latitude', 'N/A')
            longitude = store_coordinates.get('longitude', 'N/A')
            phone = business.get('display_phone', 'N/A')
            rating = business.get('rating', 'N/A')
            review_count = business.get('review_count', 'N/A')
            distance = business.get('distance', 'N/A')
            distance = round(distance / 1609.34)
            distance = f"{distance} miles"
            business_url = business.get('url', 'N/A')
            price = business.get('price', 'N/A')
            hours = business.get('business_hours', [])
            is_open_now = hours[0].get('is_open_now') if hours else 'N/A'
            google_maps_link = get_google_maps_link(address)

            store_data.append({
                'name': name,
                'address': address,
                'latitude': latitude,
                'longitude': longitude,
                'phone': phone,
                'rating': rating,
                'review_count': review_count,
                'distance': distance,
                'business_url': business_url,
                'google_maps_link': google_maps_link,
                'price': price,
                'hours': format_business_hours(hours),
                'is_open_now': is_open_now,
            })
    
    else:
        # If no businesses are found
        store_data.append({
            'name': 'N/A',
            'address': 'N/A',
            'latitude': 'N/A',
            'longitude': 'N/A',
            'phone': 'N/A',
            'rating': 'N/A',
            'review_count': 'N/A',
            'distance': 'N/A',
            'business_url': 'N/A',
            'google_maps_link': 'N/A',
            'price': 'N/A',
            'hours': 'N/A',
            'is_open_now': 'N/A',
        })

    return store_data
  
# Define a function to get store information based on user location
def find_nearby_grocery_stores_by_user_location(radius, categories, open_now):
    """
    Finds nearby grocery stores by user's current location.
    """
    # Placeholder for store data
    store_data = []

    # Get user's current location
    g = geocoder.ip('me')
    user_latitude, user_longitude = g.latlng

    # Prepare request parameters
    params = {
        'categories': categories,
        'open_now': open_now,
        'latitude': user_latitude,
        'longitude': user_longitude,
        'radius': radius,
        'limit': 5,  # Limit to 5 results
    }

    # Make the API request
    response = requests.get(YELP_URL, headers=headers, params=params)
    data = response.json()

    # Check if businesses were found
    if data.get('businesses'):
        # Sort businesses by distance
        sorted_businesses = sorted(data['businesses'], key=lambda x: x['distance'])

        # Extract and process each business
        for business in sorted_businesses:
            name = business.get('name', 'N/A')
            address = ', '.join(business['location'].get('display_address', []))
            store_coordinates = business.get('coordinates', {})
            store_latitude = store_coordinates.get('latitude', 'N/A')
            store_longitude = store_coordinates.get('longitude', 'N/A')
            phone = business.get('display_phone', 'N/A')
            rating = business.get('rating', 'N/A')
            review_count = business.get('review_count', 'N/A')
            distance = business.get('distance', 'N/A')
            # Convert distance to miles
            distance = f"{round(distance / 1609.34)} miles"
            business_url = business.get('url', 'N/A')
            price = business.get('price', 'N/A')
            hours = business.get('business_hours', [])
            is_open_now = hours[0].get('is_open_now') if hours else 'N/A'
            google_maps_link = get_google_maps_link(address)

            # Append processed data to the list
            store_data.append({
                'name': name,
                'address': address,
                'latitude': store_latitude,
                'longitude': store_longitude,
                'phone': phone,
                'rating': rating,
                'review_count': review_count,
                'distance': distance,
                'business_url': business_url,
                'google_maps_link': google_maps_link,
                'price': price,
                'hours': format_business_hours(hours),
                'is_open_now': is_open_now
            })

    else:
        # Append default "N/A" values if no businesses are found
        store_data.append({
            'name': 'N/A',
            'address': 'N/A',
            'latitude': 'N/A',
            'longitude': 'N/A',
            'phone': 'N/A',
            'rating': 'N/A',
            'review_count': 'N/A',
            'distance': 'N/A',
            'business_url': 'N/A',
            'google_maps_link': 'N/A',
            'price': 'N/A',
            'hours': 'N/A',
            'is_open_now': 'N/A',
        })

    return store_data


# Defining a function to categorize prize
def price_categorizer(price_str):
  try:
    price = float(price_str)
    if price < 3:
      return "$"
    elif 3 <= price <= 10:
      return "$$"
    elif 10 < price <= 30:
      return "$$$"
    else:
      return "$$$$"
  except (ValueError, TypeError):
    return "N/A"  # Handle cases where price is not a valid number


# Definnig a function to clean allergen filter
def clean_allergens(allergen_string):
    if allergen_string == 'N/A':  # If no allergens, return as is
        return ['N/A']
    elif isinstance(allergen_string, list):  # Check if allergen_string is a list
        return [allergen.split(':')[-1] if isinstance(allergen, str) and ':' in allergen else allergen for allergen in allergen_string]
    elif isinstance(allergen_string, str):  # Check if allergen_string is a string
        return [allergen.split(':')[-1] for allergen in allergen_string.split(',')]
    else:
        return ['N/A']  # Handle cases where allergen_string is neither a list nor a string
    
    
# Defining a function to sort the filters
def results_sorter(form):
    # Extracting data from the form
    search_query = form['search_query']
    filters = form['filters']
    address = filters.get('address', None)
    distance_in_miles = float(filters.get('distance', 0))
    distance_in_meters = int(distance_in_miles * 1609.34)  # Convert miles to meters
    
    #Set availability based on the filter value
    #print('availability: ', filters.get('availability', ''))
    if filters.get('availability', '') == "Open":
        availability = 'true'
    else:
        availability = 'false'
    
    # Call get_open_food_facts_info_by_name with the search query
    products = get_open_food_facts_info_by_name(search_query)

    # Initialize results and debug info
    filtered_products = {}
    scored_products = []  # To store products with their scores

    # Loop through each product and apply filters
    for product in products:
        product_name = product.get('product_name', 'Unknown')
        filter_results = {  # Initialize all filters with default value 'N/A'
            'name': product_name,
            'brand': product.get('brand', 'N/A'),
            'allergens': clean_allergens(product.get('allergens', 'N/A')),
            'ingredients': (product.get('ingredients', 'N/A')),
            'additives': clean_allergens(product.get('additives', 'N/A')),
            'price': 'N/A',  # Will be fetched dynamically if possible
            'caloric_value': product.get('calories', 'N/A'),
            'size': product.get('serving_size', 'N/A'),
            'fat_value': product.get('fat', 'N/A'),
            'saturated_fat_value': product.get('saturated_fat', 'N/A'),
            'carbs_value': product.get('carbohydrates', 'N/A'),
            'protein_value': product.get('proteins', 'N/A'),
            'sodium_value': product.get('sodium', 'N/A'),
            'fiber_value': product.get('fiber', 'N/A'),
            'ecoscore_grade': product.get('ecoscore_grade', 'N/A'),
            'product_url': product.get('product_url', 'N/A'),
            'image_url': product.get('image_url', 'N/A'),
        }

        filter_pass_count = 0  # Counter for filters passed

        # Brand filter
        if 'brand' in filters and filters['brand']:
            if 'brand' in product and any(b in product['brand'] for b in filters['brand']):
                filter_pass_count += 1

        # Allergen filter
        if 'allergens' in filters and filters['allergens']:
            if 'allergens' in product and not any(a in product['allergens'] for a in filters['allergens']):
                filter_pass_count += 1

        # Price filter
        if 'price' in filters and filters['price']:
            if 'plu_code' in product:
                price_info = get_prices_and_average(product['plu_code'])
                if "error" not in price_info:
                    avg_price = price_info["average_price"]
                    filter_results['price'] = avg_price  # Update with actual price value
                    categorized_price = price_categorizer(avg_price)
                    if categorized_price == filters['price']:
                        filter_pass_count += 1

        # Caloric filter
        if 'caloric_value' in filters and filters['caloric_value']:
            if 'nutriments' in product and 'energy-kcal' in product['nutriments']:
                calories = product['nutriments']['energy-kcal']
                filter_results['caloric_value'] = calories
                if calories and filters['caloric_value'] in ["Low", "Medium", "High"]:
                    filter_pass_count += 1

        # Size filter
        if 'size' in filters and filters['size']:
            if 'serving_size' in product:
                filter_results['size'] = product['serving_size']
                filter_pass_count += 1

        # Fat filter
        if 'fat_value' in filters and filters['fat_value']:
            if 'nutriments' in product and 'fat_100g' in product['nutriments']:
                fat_value = product['nutriments']['fat_100g']
                filter_results['fat_value'] = fat_value
                if fat_value:
                    filter_pass_count += 1

        # Saturated Fat filter
        if 'saturated_fat_value' in filters and filters['saturated_fat_value']:
            if 'nutriments' in product and 'saturated-fat_100g' in product['nutriments']:
                saturated_fat = product['nutriments']['saturated-fat_100g']
                filter_results['saturated_fat_value'] = saturated_fat
                if saturated_fat:
                    filter_pass_count += 1

        # Carbohydrate filter
        if 'carbs_value' in filters and filters['carbs_value']:
            if 'nutriments' in product and 'carbohydrates_100g' in product['nutriments']:
                carbohydrates = product['nutriments']['carbohydrates_100g']
                filter_results['carbs_value'] = carbohydrates
                if carbohydrates:
                    filter_pass_count += 1

        # Protein filter
        if 'protein_value' in filters and filters['protein_value']:
            if 'nutriments' in product and 'proteins_100g' in product['nutriments']:
                proteins = product['nutriments']['proteins_100g']
                filter_results['protein_value'] = proteins
                if proteins:
                    filter_pass_count += 1

        # Sodium filter
        if 'sodium_value' in filters and filters['sodium_value']:
            if 'nutriments' in product and 'sodium_100g' in product['nutriments']:
                sodium = product['nutriments']['sodium_100g']
                filter_results['sodium_value'] = sodium
                if sodium:
                    filter_pass_count += 1

        # Fiber filter
        if 'fiber_value' in filters and filters['fiber_value']:
            if 'nutriments' in product and 'fiber_100g' in product['nutriments']:
                fiber = product['nutriments']['fiber_100g']
                filter_results['fiber_value'] = fiber
                if fiber:
                    filter_pass_count += 1

        # Ecoscore filter
        if 'Ecoscore_Grade' in filters and filters['Ecoscore_Grade']:
            if 'ecoscore_grade' in product:
                ecoscore = product['ecoscore_grade'].upper()  # Capitalize ecoscore grade
                filter_results['ecoscore_grade'] = ecoscore
                if ecoscore == filters['Ecoscore_Grade'].upper():  # Match case for comparison
                    filter_pass_count += 1
            else:
                filter_results['ecoscore_grade'] = "N/A"

        # Skip products with filter_pass_count = 0
        #if filter_pass_count == 0:
        #    continue

        # Fetch location info based on availability of address
        if address:
            address_info = find_nearby_grocery_stores_by_address(
                radius=distance_in_meters,
                categories="grocery, supermarket",
                open_now=availability,
                address=address
            )
            
            # Getting user coordinates
            latitude, longitude = get_coordinates(address)
            filter_results['location_info'] = address_info
            filter_results['user_coordinates'] = {latitude, longitude}
            
        else:
            address_info = find_nearby_grocery_stores_by_user_location (
                radius=distance_in_meters,
                categories="grocery, supermarket",
                open_now=availability,
            )
            
            # Getting User coordinates
            g = geocoder.ip('me')
            latitude, longitude = g.latlng
            filter_results['user_coordinates'] = {latitude, longitude}
        
            
        #print('address_info: ', address_info)
        #print('radius: ', distance_in_meters, 'categories: grocery, supermarket open_now: ', availability, '. address: ', address)
        
        # Add location info to filter results
        filter_results['location_info'] = address_info


        # append info to container
        filtered_products[product_name] = filter_results

        # Add product to scored list if at least one filter is passed
        scored_products.append({'product': product, 'score': filter_pass_count})


    # Sort products by score in descending order (highest recommended first)
    scored_products.sort(key=lambda x: x['score'], reverse=True)

    # Sort debug info by score
    sorted_debug_info = {
        item['product']['product_name']: filtered_products[item['product']['product_name']]
        for item in scored_products
    }

    # Return results and detailed filter information
    return {
        "filter_results": sorted_debug_info,  # Sorted debug info by score
        #"debug": products,
        #"scores": [{item['product']['product_name']: item['score']} for item in scored_products]
    }


# Defining a function to handle a csv for popular products
def popular_produce(csv_relative_path):
    """
    Fetch details for popular produce based on PLU codes from a CSV file in the static directory.

    Args:
        csv_relative_path (str): Relative path to the CSV file within the static directory.

    Returns:
        list[dict]: A list of dictionaries with produce data.
    """
    # Resolve the full path to the static file
    csv_path = os.path.join(settings.STATICFILES_DIRS[0], csv_relative_path)

    # Debugging: Print the resolved path
    #print('CSV path is:', csv_path)

    # Read the CSV file
    #produce_df = pd.read_csv(csv_path)
    produce_data = []
    try:
        with open(csv_path, mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                produce_data.append(row)
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
    
    return produce_data

import json

def serialize_products(products):
    return json.dumps([
        {
            "name": product["name"],
            "image_url": product["image_url"],
            "location_info": {
                "latitude": product["location_info"]["latitude"],
                "longitude": product["location_info"]["longitude"],
                "name": product["location_info"]["name"]
            }
        }
        for product in products
    ])


