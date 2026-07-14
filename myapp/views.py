from django.shortcuts import render, HttpResponse
from .models import TodoItem

def home(request):
    return render(request, "home.html")

def todos(request):
    items = TodoItem.objects.all()
    return render(request, "todos.html", {"todos": items})

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from myapp.models import IMURecord
from myapp.serializers import IMURecordSerializer

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return

collection_paused = False

class IMURecordViewSet(viewsets.ModelViewSet):
    queryset = IMURecord.objects.all().order_by('timestamp')
    serializer_class = IMURecordSerializer
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def create(self, request, *args, **kwargs):
        if collection_paused:
            return Response({'status': 'paused, data ignored'}, status=status.HTTP_200_OK)
        return super().create(request, *args, **kwargs)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import time

def current_time(request):
    return JsonResponse({'epoch': int(time.time())})

def collection_status(request):
    return JsonResponse({'paused': collection_paused})

@csrf_exempt
def pause_collection(request):
    global collection_paused
    collection_paused = True
    return JsonResponse({'status': 'paused'})

@csrf_exempt
def resume_collection(request):
    global collection_paused
    collection_paused = False
    return JsonResponse({'status': 'resumed'})