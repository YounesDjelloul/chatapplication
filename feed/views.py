from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import Post, PostLike, PostComment
from django.db import transaction
import json

# Create your views here.

class PostsListView(APIView):
    permission_classes = [IsAuthenticated]
    post_serializer_class = PostSerializer
    media_serializer_class = PostMediaSerializer

    def get(self, request):
        posts = Post.objects.all()
        serializer = self.post_serializer_class(posts, many=True)

        return Response(serializer.data, status.HTTP_200_OK)

    @transaction.atomic
    def post(self, request):
        data = request.data.copy()

        profile_instance = request.user.profile
        post_media = data.pop('post_media', [])

        post_serializer = self.post_serializer_class(data=data)
        if post_serializer.is_valid():
            post_instance = post_serializer.save(profile=profile_instance)

            for media in post_media:
                media_serializer = self.media_serializer_class(data={"file": media})
                if media_serializer.is_valid():
                    media_serializer.save(post=post_instance)
                else:
                    transaction.set_rollback(True)
                    return Response(media_serializer.errors, status.HTTP_400_BAD_REQUEST)
            
            return Response(post_serializer.data, status.HTTP_201_CREATED)

        return Response(post_serializer.errors, status.HTTP_400_BAD_REQUEST)
    
class PostDetailsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer

    def get(self, request, pk):
        post_instance = Post.objects.safe_get(id=pk)

        if post_instance:
            serializer = self.serializer_class(post_instance)
            return Response(serializer.data, status.HTTP_200_OK)
        
        return Response('Post not found', status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        post_instance = Post.objects.safe_get(id=pk)

        if post_instance:
            serializer = self.serializer_class(data=request.data, instance=post_instance, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status.HTTP_200_OK)

            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        return Response('Post not found', status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        post_instance = Post.objects.safe_get(id=pk)

        if post_instance:
            post_instance.delete()
            return Response('Post deleted Successfully', status.HTTP_200_OK)

        return Response('Post not found', status.HTTP_400_BAD_REQUEST)
    
class PostLikesView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PostLikeSerializer

    def get(self, request, pk):
        post_instance = Post.objects.safe_get(id=pk)

        if post_instance:
            post_likes = PostLike.objects.filter(post=post_instance)
            serializer = self.serializer_class(post_likes, many=True)
            return Response(serializer.data, status.HTTP_200_OK)

        return Response('Post not found', status.HTTP_400_BAD_REQUEST)

    def post(self, request, pk):
        post_instance = Post.objects.safe_get(id=pk)
        profile = request.user.profile

        if post_instance:
            action = post_instance.toggle_like(profile)
            return Response(f'Like {action} Successfully', status.HTTP_200_OK)

        return Response('Post not found', status.HTTP_400_BAD_REQUEST)
    
class PostCommentsView(APIView):
    permission_classes = [IsAuthenticated]
    serialializer_class = PostCommentSerializer

    def get(self, request, pk):
        post_instance = Post.objects.safe_get(id=pk)

        if post_instance:
            post_comments = post_instance.parent_comments()
            print(post_comments)
            serializer = self.serialializer_class(post_comments, many=True)
            
            return Response(serializer.data, status.HTTP_200_OK)

        return Response('Post not found', status.HTTP_400_BAD_REQUEST)

    def post(self, request, pk):
        data = json.loads(json.dumps(request.data.copy()))
        commentParentId = data.pop('parent', None)
        commentParent = PostComment.objects.safe_get(id=commentParentId)
        post_instance = Post.objects.safe_get(id=pk)
        profile = request.user.profile

        if (commentParentId and not commentParent) or not post_instance:
            return Response('Post not found', status.HTTP_400_BAD_REQUEST)

        serializer = self.serialializer_class(data=data)

        if serializer.is_valid():
            serializer.save(profile=profile, parent=commentParent, post=post_instance)
            return Response(serializer.data, status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    
class PostCommentDetailsView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request, post_pk, comment_pk):
        profile = request.user.profile
        
        post_instance = Post.objects.safe_get(id=post_pk)
        comment_instance = PostComment.objects.safe_get(id=comment_pk)

        if post_instance and comment_instance:
            if post_instance.profile == profile or comment_instance.profile == profile:
                comment_instance.delete()
                return Response('Comment deleted Successfully', status.HTTP_200_OK)
            
            return Response('Action not allowed', status.HTTP_400_BAD_REQUEST)
        
        return Response('Post or comment not found', status.HTTP_400_BAD_REQUEST)