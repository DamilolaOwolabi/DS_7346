import pandas as pd
import os
import requests
from django.conf import settings
from django.templatetags.static import static  # Utility to resolve static file paths

def get_open_food_facts_info(grocery_name, code):
    #declaring variables
    produce_items = []
    plu_code = code
    produce_name = grocery_name
    
    # Fetch product data from Open Food Facts API
    url = f'https://world.openfoodfacts.org/api/v0/product/{plu_code}.json'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 1:  # Product found
            product = data.get('product', {})
            produce_items.append({
                'produce_name': produce_name,
                'product_name': product.get('product_name_en', 'N/A'),
                'image_url': product.get('image_url', ''),
                'calories': product.get('nutriments', {}).get('energy-kcal_value', 'N/A'),
                'fat': product.get('nutriments', {}).get('fat', 'N/A'),
                'sugars': product.get('nutriments', {}).get('sugars', 'N/A'),
                'proteins': product.get('nutriments', {}).get('proteins', 'N/A'),
            })
        else:
            produce_items.append({
                'produce_name': produce_name,
                'product_name': 'N/A',
                'image_url': '',
                'calories': 'N/A',
                'fat': 'N/A',
                'sugars': 'N/A',
                'proteins': 'N/A',
            })
            
    return produce_items
    

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
    produce_df = pd.read_csv(csv_path)
    info = []

    for _, row in produce_df.iterrows():
        plu_code = row['PLU Code']
        produce_name = row['Produce Item']
        #getting data from the get_open_food_facts_info() function
        info += get_open_food_facts_info(produce_name, plu_code)

    return info
