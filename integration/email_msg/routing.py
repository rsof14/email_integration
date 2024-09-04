from django.urls import path

from .consumers import EmailConsumer


ws_urlpatterns = [
    path('ws/email/', EmailConsumer.as_asgi())
]