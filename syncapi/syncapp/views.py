"""
Author: Ali Riza Girisen
Date: 17/11/2023
"""
import configparser
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .sync.sync_ad import sync_data
from .sync.test_conn import test_connections
import json

@csrf_exempt
def sync_api(request): 
    
    if request.method =='POST':
        try:
            data = json.loads(request.body.decode('utf-8'))

            ad_config = data.get('ad_config',{})
            ldap_config = data.get('ldap_config',{})
            pref_config = data.get('pref_config',{})
            input_dn = data.get('input_dn')

            result = sync_data(ad_config, ldap_config, pref_config, input_dn, True)
            return JsonResponse(result, safe=False)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format in the request body'},status=400)
    else:
        return JsonResponse({'error':'Invalid request method'})

@csrf_exempt
def test_api(request):
    if request.method =='POST':
        try:
            data = json.loads(request.body.decode('utf-8'))

            ad_config = data.get('ad_config',{})
            ldap_config = data.get('ldap_config',{})
            result = test_connections(ad_config, ldap_config)

            return JsonResponse(result, safe=False)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format in the request body'},status=400)
    else:
        return JsonResponse({'error':'Invalid request methd'})
