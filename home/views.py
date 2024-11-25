from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import GroceryPreferenceForm # our user input page
from .utils.recommendation_engine import get_recommendations #getting the recommendation engine function
from .utils.utils import * # getting the popular produce function
from django.templatetags.static import static  # To resolve static file paths
from django.conf import settings
from django.core.paginator import Paginator # Auto create pages
from django.db import models
import json

# Create your views here.

# Model to save queries (Add this to models.py if not already created)
class QueryLog(models.Model):
    query_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.query_text


# Function to save the query to the database
def save_query(query_text):
    QueryLog.objects.create(query_text=query_text)

def index(request):
    # Page from the theme 
    return render(request, 'pages/index.html')

def grocery_recommendation_view(request):
    if request.method == 'POST':
        # Check if the submit button was clicked
        submit_button_clicked = request.POST.get('submit_button', False)

        if submit_button_clicked:
            # Get the search query and filters
            search_query = request.POST.get('search_query', '').strip()
            selected_filters = {
                'brand': request.POST.getlist('brand'),
                'size': request.POST.get('size'),
                'address': request.POST.get('address'),
                'distance': request.POST.get('distance'),
                'allergens': request.POST.getlist('allergens'),
                'price': request.POST.get('price'),
                'availability': request.POST.get('availability'),
                'caloric_value': request.POST.get('caloric_value'),
                'fat_value': request.POST.get('fat_value'),
                'saturated_fat_value': request.POST.get('saturated_fat_value'),
                'carbs_value': request.POST.get('carbs_value'),
                'protein_value': request.POST.get('protein_value'),
                'sodium_value': request.POST.get('sodium_value'),
                'fiber_value': request.POST.get('fiber_value'),
                'Ecoscore_Grade': request.POST.get('Ecoscore_Grade'),
            }

            # Combine search query and filters
            combined_data = {
                'search_query': search_query,
                'filters': selected_filters,
            }

            # Clear old cached results
            for key in list(request.session.keys()):
                if key.startswith("results_"):
                    del request.session[key]

            # Store new query in the session
            request.session['combined_data'] = combined_data

            return redirect('grocery_results_view')

    # Default GET behavior
    csv_relative_path = 'documents/popular_produce_plu_codes.csv'
    form = popular_produce(csv_relative_path)
    return render(request, 'pages/input_form.html', {'form': form, 'show_sidebar': False})


def grocery_results_view(request):
    # Get the current query from the session
    combined_data = request.session.get('combined_data', None)

    if not combined_data:
        # Redirect to search form if no query exists in the session
        return redirect('grocery_recommendation_view')

    # Generate a unique key for the current query
    query_key = f"results_{hash(json.dumps(combined_data))}"

    # Check if cached results exist for this query
    cached_results = request.session.get(query_key, None)

    if cached_results:
        # Use cached results
        results_data = cached_results
        #print("Using cached results")
    else:
        # Call API and cache results
        #print("Calling API and caching results")
        results_data = results_sorter(combined_data)
        request.session[query_key] = results_data

    # Extract products
    products = list(results_data["filter_results"].values())

    # Convert sets to lists
    for product in products:
        if "user_coordinates" in product and isinstance(product["user_coordinates"], set):
            product["user_coordinates"] = list(product["user_coordinates"])

    # Pagination
    paginator = Paginator(products, 1)  # 1 product per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Serialize JSON
    products_json = json.dumps(list(page_obj.object_list))
    print(products_json)

    return render(
        request,
        "pages/results.html",
        {"products": page_obj, "products_json": products_json},
    )
