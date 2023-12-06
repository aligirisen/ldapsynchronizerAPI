"""
Author: Ali Riza Girisen
Date: 17/11/2023
"""
import configparser
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .sync.sync_ad import sync_data, sync_event, progress_lock, MyThread
from .sync.test_conn import test_connections
import json, os
import threading

@csrf_exempt
def sync_api(request): 
    
    if request.method =='POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            ad_config = data.get('ad_config',{})
            ldap_config = data.get('ldap_config',{})
            pref_config = data.get('pref_config',{})
            input_dn = data.get('input_dn')

            if sync_event.is_set():
                with progress_lock:
                    progress_thread = MyThread(target=MyThread.run)
                    progress_thread.start()
                return JsonResponse({'message': f'Please wait... Sync operation is already in progress {progress_thread.result:.0f}%. Started at {progress_thread.utc}'})
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

@csrf_exempt
def status_api(request):
    if request.method == 'GET':
        try:
            if sync_event.is_set():
                with progress_lock:
                    progress_thread = MyThread(target=MyThread.run)
                    progress_thread.start()
                return JsonResponse({'message': f'Started at {progress_thread.utc}. Progress: {progress_thread.result:.0f}%'})
            else:
                file_path = 'output.txt'
                if os.path.exists(file_path):
                    output = ""
                    with open(file_path, 'r') as file:
                        for line_number, line in enumerate(file, start=1):
                            output += line
                    os.remove(file_path)

                return JsonResponse({'message': 'There is no more existing operation'})
            return JsonResponse(result, safe=False)
        except json.JSONDecodeError:
            return JsonResponse({'error': ''},status=400)
    else:
        return JsonResponse({'error':'Invalid request method'})
