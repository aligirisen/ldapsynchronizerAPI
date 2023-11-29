"""
Author: Ali Riza Girisen
Date: 17/11/2023
"""
import configparser
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .sync.sync_ad import sync_data, sync_event
from .sync.test_conn import test_connections
import json
import threading

@csrf_exempt
def sync_api(request): 
    global sync_in_progress
    
    if request.method =='POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            ad_config = data.get('ad_config',{})
            ldap_config = data.get('ldap_config',{})
            pref_config = data.get('pref_config',{})
            input_dn = data.get('input_dn')

            if sync_event.is_set():
                return JsonResponse({'message': 'Please wait... Sync operation is already in progress'})
            sync_thread = threading.Thread(target=sync_data, args=(ad_config, ldap_config, pref_config, input_dn, True))
            sync_thread.start()

            return JsonResponse ({'message': 'Sync operation is in progress'}, safe=False)

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
        return JsonResponse({'error':'Invalid request method'})
