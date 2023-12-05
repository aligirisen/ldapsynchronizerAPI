from django.urls import path
from .views import sync_api, test_api, status_api

urlpatterns = [
        path('sync/', sync_api, name='sync_api'),
        path('test/', test_api, name='test_api'),
        path('sync/status/', status_api, name='status_api')
        ]

