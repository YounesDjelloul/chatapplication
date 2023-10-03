import pytest
import os
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import *
from django.urls import reverse
from accounts.tests import api_client, logged_api_client, create_user

# Create your tests here.

def image_for_test():
    media_path = '/home/younesdjelloul/Desktop/Documents/profile_picture.jpg'
    media_name = os.path.basename(media_path)
    media_content = open(media_path, 'rb').read()
    
    media = SimpleUploadedFile(media_name, media_content, content_type='image/jpg')

    return media

@pytest.mark.parametrize(
    'caption, media, status_code', [
        ('', ['hey'], 400),
        ('This is caption', ['hey'], 400),
        ('This is caption', [image_for_test()], 201),
        ('This is caption', [], 201),
        ('This is caption', [image_for_test(), image_for_test()], 201),
    ]
)
@pytest.mark.django_db
def test_create_post(caption, media,status_code, logged_api_client):
    client, user = logged_api_client

    url = reverse('posts')

    data = {
        'caption': caption,
        'post_media': media
    }

    response = client.post(url, data, format='multipart')
    assert response.status_code == status_code
    if status_code == 201:
        assert Post.objects.all().count() == 1
        assert Post.objects.first().profile == user.profile
        assert Post.objects.first().likes() == 0
        assert PostMedia.objects.filter(post=Post.objects.first()).count() == len(media)

@pytest.mark.django_db
def test_get_all_posts(logged_api_client):
    client, user = logged_api_client
    url = reverse('posts')

    post = Post.objects.create(profile=user.profile, caption='This is caption')

    response = client.get(url)

    assert response.status_code == 200
    assert len(response.json()) == 1

@pytest.mark.parametrize(
    'post_id, status_code', [
        (0, 400),
        (1, 200),
    ]
)
@pytest.mark.django_db
def test_get_one_post(post_id, status_code, logged_api_client):
    client, user = logged_api_client
    post = Post.objects.create(profile=user.profile, caption='This is caption')

    url = reverse('post_details', args=[post_id])

    response = client.get(url)

    assert response.status_code == status_code
    if status_code == 200:
        assert response.json()['profile']['id'] == user.profile.id
        assert response.json()['id'] == post.id

@pytest.mark.parametrize(
    'post_id, caption, status_code', [
        (0, '', 400),
        (1, '', 400),
        (0, 'This is new caption', 400),
        (1, 'This is new caption', 200),
    ]
)
@pytest.mark.django_db
def test_update_one_post(post_id, caption, status_code, logged_api_client):
    client, user = logged_api_client
    Post.objects.create(profile=user.profile, caption='This is caption')

    url = reverse('post_details', args=[post_id])

    data = {
        "caption": caption
    }

    response = client.patch(url, data)

    assert response.status_code == status_code
    if status_code == 200:
        assert Post.objects.first().caption == caption

@pytest.mark.parametrize(
    'post_id, status_code', [
        (0, 400),
        (1, 200),
    ]
)
@pytest.mark.django_db
def test_delete_one_post(post_id, status_code, logged_api_client):
    client, user = logged_api_client
    post = Post.objects.create(profile=user.profile, caption='This is caption')
    PostMedia.objects.create(post=post, file=image_for_test())

    url = reverse('post_details', args=[post_id])

    response = client.delete(url)

    assert response.status_code == status_code
    if status_code == 200:
        assert Post.objects.all().count() == 0
        assert PostMedia.objects.all().count() == 0

@pytest.mark.parametrize(
    'post_id, likes, status_code', [
        (0, 0, 400),
        (1, 0, 200),
        (1, 1, 200),
    ]
)
@pytest.mark.django_db
def test_toggle_post_like(post_id, likes, status_code, logged_api_client):
    client, user = logged_api_client
    post = Post.objects.create(profile=user.profile, caption='This is caption')

    if likes == 0:
        PostLike.objects.create(post=post, profile=user.profile)

    url = reverse('post_likes', args=[post_id])
    response = client.post(url)

    assert response.status_code == status_code
    if status_code == 200:
        assert Post.objects.first().likes() == likes
        if likes == 0:
            assert Post.objects.first().is_profile_in_likes(user.profile) == False
        
        if likes == 1:
            assert Post.objects.first().is_profile_in_likes(user.profile) == True

@pytest.mark.parametrize(
    'post_id, status_code', [
        (0, 400),
        (1, 200),
    ]
)
@pytest.mark.django_db
def test_get_post_likes(post_id, status_code, logged_api_client):
    client, user = logged_api_client
    post = Post.objects.create(profile=user.profile, caption='This is caption')

    PostLike.objects.create(post=post, profile=user.profile)

    url = reverse('post_likes', args=[post_id])

    response = client.get(url)

    assert response.status_code == status_code
    if status_code == 200:
        assert post.likes() == len(response.json())

@pytest.mark.parametrize(
    'post_id, commentContent, status_code', [
        (0, '', 400),
        (1, '', 400),
        (1, 'Comment Content', 201),
    ]
)
@pytest.mark.django_db
def test_create_post_comment(post_id, commentContent, status_code, logged_api_client):
    client, user = logged_api_client
    Post.objects.create(profile=user.profile, caption='This is caption')

    data = {
        "content": commentContent,
    }

    url = reverse('post_comments', args=[post_id])
    response = client.post(url, data)
    print(response.data)
    assert response.status_code == status_code

    if status_code == 201:
        assert PostComment.objects.all().count() == 1


@pytest.mark.parametrize(
    'parent_id, status_code', [
        (0, 400),
        (1, 201),
    ]
)
@pytest.mark.django_db
def test_create_post_comment_reply(parent_id, status_code, logged_api_client):
    client, user = logged_api_client
    post = Post.objects.create(profile=user.profile, caption='This is caption')

    PostComment.objects.create(post=post, profile=user.profile, content='This is parent content')

    data = {
        "parent": parent_id,
        "content": 'This is child content',
    }

    url = reverse('post_comments', args=[post.id])
    response = client.post(url, data)
    
    assert response.status_code == status_code
    if status_code == 201:
        assert PostComment.objects.all().count() == 2

@pytest.mark.parametrize(
    'post_id, comments_count, status_code', [
        (0, 0, 400),
        (1, 0, 200),
        (1, 1, 200),
    ]
)
@pytest.mark.django_db
def test_get_post_comments(post_id, comments_count, status_code, logged_api_client):
    client, user = logged_api_client
    post = Post.objects.create(profile=user.profile, caption='This is caption')

    if comments_count != 0:
        parentComment = PostComment.objects.create(post=post, profile=user.profile, content='This is parent content')
        PostComment.objects.create(post=post, profile=user.profile, parent=parentComment, content='This is parent content')

    url = reverse('post_comments', args=[post_id])
    response = client.get(url)
    
    assert response.status_code == status_code
    if status_code == 200:
        assert len(response.json()) == comments_count

@pytest.mark.parametrize(
    'post_id, comment_id, status_code', [
        (0, 0, 400),
        (0, 1, 400),
        (1, 0, 400),
        (1, 1, 200),
    ]
)
@pytest.mark.django_db
def test_delete_post_comment(post_id, comment_id, status_code, logged_api_client):
    client, user = logged_api_client

    post = Post.objects.create(profile=user.profile, caption='This is caption')
    PostComment.objects.create(post=post, profile=user.profile, content='This is parent content')

    url = reverse('post_comment_details', args=[post_id, comment_id])
    response = client.delete(url)
    
    assert response.status_code == status_code
    if status_code == 200:
        assert PostComment.objects.all().count() == 0

@pytest.mark.django_db
def test_delete_post_comment_without_permission(create_user, logged_api_client):
    client, user = logged_api_client

    another_user = create_user()

    post = Post.objects.create(profile=another_user.profile, caption='This is caption')
    PostComment.objects.create(post=post, profile=another_user.profile, content='This is parent content')

    url = reverse('post_comment_details', args=[1, 1])
    response = client.delete(url)
    
    assert response.status_code == 400
    assert PostComment.objects.all().count() == 1