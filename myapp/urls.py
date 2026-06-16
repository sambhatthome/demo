from django.urls import path, include
from . import views
from .views import current_time
from rest_framework.routers import DefaultRouter
from myapp.views import IMURecordViewSet

router = DefaultRouter()
router.register(r'imu', IMURecordViewSet)

urlpatterns = [
    path("", views.home, name="home"),
    path("todos/", views.todos, name="Todos"),
    path('time/', current_time),
] + router.urls
