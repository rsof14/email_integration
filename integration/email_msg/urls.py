from django.urls import path, include
from .views import index, main, all_emails

urlpatterns = [
    path('email', index),
    path('', main)
]