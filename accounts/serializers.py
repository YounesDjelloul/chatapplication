from rest_framework import serializers
from .models import User, Profile, Like
from feed.models import Post

class UserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def validate(self, data):
        if data.get('password1') != data.get('password2'):
            raise serializers.ValidationError('Passwords didn\'t match ')
        
        return data
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data, password=validated_data.get('password1'))
    
    def update(self, instance, validated_data):

        for user_property, value in validated_data.items():
            setattr(instance, user_property, value)

        instance.save()
        return instance
    
class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Profile
        fields = '__all__'

    def validate(self, data):
        for attribute, value in data.items():
            if not value or len(value) == 0:
                raise serializers.ValidationError(f'{attribute} cannot be null')
        
        return data
    
    def update(self, instance, validated_data):
        for profile_property, value in validated_data.items():
            setattr(instance, profile_property, value)

        instance.save()
        return instance
    
class LikeSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    
    class Meta:
        model = Like
        fields = ['profile', 'post']

    def validate(self, data):
        return data
    
    def create(self, validated_data):
        return Like.objects.create(profile=validated_data.get('profile_instance'), post=validated_data.get('post_instance'))