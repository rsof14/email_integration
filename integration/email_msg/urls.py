from django.urls import path, include
from .views import index, main

urlpatterns = [
    path('email', index),
    path('', main)
]