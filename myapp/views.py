from django.shortcuts import render, HttpResponse
from .models import TodoItem

# Create your views here.

def home(request):
    return render(request, "home.html")

def todos(request):
    items = TodoItem.objects.all()
    return render(request, "todos.html", {"todos": items})

from rest_framework import viewsets
from myapp.models import IMURecord
from myapp.serializers import IMURecordSerializer

class IMURecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IMURecord.objects.all().order_by('timestamp')
    serializer_class = IMURecordSerializer