from rest_framework import serializers
from .models import *
from accounts.serializers import ProfileSerializer

class PostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = ['id', 'file']

class PostSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    post_media = PostMediaSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'profile', 'caption', 'likes', 'created_at', 'post_media']

    def validate(self, data):
        for attribute, value in data.items():
            if not value or len(value) == 0:
                raise serializers.ValidationError(f'{attribute} cannot be null')
        
        return data
    
    def create(self, validated_data):
        return Post.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        for profile_property, value in validated_data.items():
            setattr(instance, profile_property, value)

        instance.save()
        return instance
    
class PostCommentSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = PostComment
        fields = ['id', 'profile', 'post', 'parent', 'created_at', 'content', 'children']
        read_only_fields = ['profile', 'post']

    def validate(self, data):
        for attribute, value in data.items():
            if not value or len(value) == 0:
                raise serializers.ValidationError(f'{attribute} cannot be null')
        
        return data
    
    def create(self, validated_data):
        return PostComment.objects.create(**validated_data)
    
    def get_children(self, obj):
        serializer = PostCommentSerializer(obj.children(), many=True)
        return serializer.data

class PostLikeSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = PostLike
        fields = ['id', 'profile']