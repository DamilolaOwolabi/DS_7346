from django.urls import path

from . import views

urlpatterns = [
    #path('', views.index, name='index'),
    path('', views.grocery_recommendation_view, name='grocery_search'),
    path('results/', views.grocery_results_view, name='grocery_results_view'),
]
