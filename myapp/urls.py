from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("todos/", views.todos, name = "Todos")
]

from rest_framework.routers import DefaultRouter
from myapp.views import IMURecordViewSet

router = DefaultRouter()
router.register(r'imu', IMURecordViewSet)

urlpatterns = router.urls