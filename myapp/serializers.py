from rest_framework import serializers
from myapp.models import IMURecord

class IMURecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = IMURecord
        fields = '__all__'