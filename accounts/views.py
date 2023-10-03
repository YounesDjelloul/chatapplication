from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, ProfileSerializer, LikeSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import User, Profile, Like
from feed.models import Post

# Create your views here.

class AccountsListView(APIView):
    serializer_class = UserSerializer

    def get(self, request):
        users = User.objects.all()
        serializer = self.serializer_class(users, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)

        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    
class AccountDetailView(APIView):
    authentication_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status.HTTP_200_OK)
    
    def delete(self, request):
        request.user.delete()
        return Response("User Deleted Successfully", status.HTTP_200_OK)
    
    def patch(self, request):
        serializer = self.serializer_class(data=request.data, instance=request.user, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    
class ProfileDetailView(APIView):
    serializer_class = ProfileSerializer

    def get(self, request, pk):
        profile = Profile.objects.safe_get(id=pk)

        if profile:
            serializer = self.serializer_class(profile)
            return Response(serializer.data, status.HTTP_200_OK)
        
        return Response('Profile not found', status.HTTP_404_NOT_FOUND)
    
    def patch(self, request, pk):
        profile = Profile.objects.safe_get(id=pk)
        
        if profile:
            serializer = self.serializer_class(data=request.data, instance=profile, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status.HTTP_200_OK)
            
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        
        return Response('Profile not found', status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, pk):
        profile = Profile.objects.safe_get(id=pk)
        
        if profile:
            profile.delete()
            return Response("User Deleted Successfully", status.HTTP_200_OK)
        
        return Response('Profile not found', status.HTTP_404_NOT_FOUND)
    
class LikesListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LikeSerializer

    def get(self, request):
        profile_likes = Like.objects.filter(profile=request.user.profile)
        serializer = self.serializer_class(profile_likes, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    def post(self, request):
        post = Post.objects.safe_get(id=request.data.get('post'))

        if post:
            serializer = self.serializer_class(data=request.data)

            if serializer.is_valid():
                serializer.save(profile_instance=request.user.profile, post_instance=post)
                return Response(serializer.data, status.HTTP_201_CREATED)

            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        
        return Response('Post not found', status.HTTP_404_NOT_FOUND)
    
class LikesDetailView(APIView):

    authentication_classes = [IsAuthenticated]
    serializer_class = LikeSerializer

    def get(self, request, pk):
        like_instance = Like.objects.safe_get(id=pk)

        if like_instance:
            serializer = self.serializer_class(like_instance)
            return Response(serializer.data, status.HTTP_200_OK)
        
        return Response('Like not found', status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, pk):
        like_instance = Like.objects.safe_get(id=pk)

        if like_instance:
            like_instance.delete()
            return Response('Like deleted Successfully', status.HTTP_200_OK)
        
        return Response('Like not found', status.HTTP_404_NOT_FOUND)