from django.urls import path
from .views import create_link_token, exchange_public_token

urlpatterns = [
    path('create-link-token/', create_link_token, name='create_link_token'),
    path('exchange-token/', exchange_public_token, name='exchange_public_token'),
]
