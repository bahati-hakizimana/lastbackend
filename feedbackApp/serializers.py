# serializers.py
from rest_framework import serializers
from .models import Feedback
from userApp.models import CustomUser

class FeedbackSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = Feedback
        fields = ['id','user', 'request', 'feedback']

    def create(self, validated_data):
        return Feedback.objects.create(**validated_data)
