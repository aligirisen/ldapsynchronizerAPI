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
                return JsonResponse({'status': 'InProgress', 'message': f'Please wait... Synchronization progress is already in progress' ,'started_at':progress_thread.utc ,'progress': f'{progress_thread.result:.0f}%'})
            sync_thread = threading.Thread(target=sync_data, args=(ad_config, ldap_config, pref_config, input_dn, True))
            sync_thread.start()

            return JsonResponse ({'status': 'Started', 'message': 'Synchronization progress has been started'}, safe=False)

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
        #try:
        if sync_event.is_set():
            with progress_lock:
                progress_thread = MyThread(target=MyThread.run)
                progress_thread.start()
            return JsonResponse({'status': 'InProgress', 'started_at':progress_thread.utc ,'progress': f'{progress_thread.result:.0f}%'})
        else:
            file_path = 'output.json'
            if os.path.exists(file_path):
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    data['status'] = 'Success'
                os.remove(file_path)
                return JsonResponse(data)

            return JsonResponse({'status': 'NotExist' , 'message': 'There is no more existing process'})
        return JsonResponse(result, safe=False)
        #except json.JSONDecodeError:
        #    return JsonResponse({'error': ''},status=400)
    else:
        return JsonResponse({'error':'Invalid request method'})
