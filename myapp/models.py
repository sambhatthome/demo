from django.db import models

# Create your models here.

class TodoItem(models.Model):
    title = models.CharField(max_length = 200)
    completed = models.BooleanField(default = False)

from django.db import models

class IMURecord(models.Model):
    timestamp = models.DateTimeField()
    ax_mg = models.IntegerField()
    ay_mg = models.IntegerField()
    az_mg = models.IntegerField()
    gx_dps = models.IntegerField()
    gy_dps = models.IntegerField()
    gz_dps = models.IntegerField()
    activity = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.timestamp} - {self.activity}"