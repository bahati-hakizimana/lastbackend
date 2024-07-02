# serializers.py
from rest_framework import serializers
from .models import Blog
import base64

class BlogSerializer(serializers.ModelSerializer):
    picture = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Blog
        fields = ['id', 'content', 'author', 'picture', 'created_at']

    def create(self, validated_data):
        picture_data = validated_data.pop('picture', None)
        blog = Blog.objects.create(**validated_data)
        if picture_data:
            try:
                picture_binary = base64.b64decode(picture_data)
                blog.picture = picture_binary
                blog.save()
            except Exception as e:
                raise serializers.ValidationError(f"Invalid picture data: {str(e)}")
        return blog