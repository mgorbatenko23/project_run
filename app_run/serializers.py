from app_run.models import Run
from rest_framework import serializers


class RunSerializer(serializers.ModelSerializer):
    class Meta:
        model = Run
        fields = ['id', 'comment', 'created_at']