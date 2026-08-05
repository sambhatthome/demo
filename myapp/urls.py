from django.urls import path, include
from . import views
from .views import current_time, collection_status, pause_collection, resume_collection, imu_batch
from rest_framework.routers import DefaultRouter
from myapp.views import IMURecordViewSet


router = DefaultRouter()
router.register(r'imu', IMURecordViewSet)

urlpatterns = [
    path("", views.home, name="home"),
    path("todos/", views.todos, name="Todos"),
    path('time/', current_time),
    path('status/', collection_status),
    path('pause/', pause_collection),
    path('resume/', resume_collection),
    path('imu/batch/', imu_batch),
] + router.urls

