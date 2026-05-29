from django.contrib import admin
from .models import TodoItem
from myapp.models import IMURecord

# Register your models here.

admin.site.register(TodoItem)
admin.site.register(IMURecord)