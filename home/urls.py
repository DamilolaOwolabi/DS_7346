from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('grocery_search/', views.grocery_recommendation_view, name='grocery_search'),
]
