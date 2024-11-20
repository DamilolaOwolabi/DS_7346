from django.shortcuts import render
from django.http import HttpResponse
from .forms import GroceryPreferenceForm # our user input page
from .utils.recommendation_engine import get_recommendations #getting the recommendation engine function
from .utils.utils import * # getting the popular produce function
from django.templatetags.static import static  # To resolve static file paths
from django.conf import settings

# Create your views here.

def index(request):

    # Page from the theme 
    return render(request, 'pages/index.html')


def grocery_recommendation_view(request):

    # Get popular produce data
    csv_relative_path = 'documents/popular_produce_plu_codes.csv'  # Relative to static directory
    form = popular_produce(csv_relative_path)
    
    return render(request, 'pages/input_form.html', {'form': form, 'show_sidebar': False})