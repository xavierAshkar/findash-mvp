from django.urls import path
from .views import create_link_token

urlpatterns = [
    path('create-link-token/', create_link_token, name='create_link_token'),
]
