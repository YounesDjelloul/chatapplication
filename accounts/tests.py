import pytest
import random
from .models import *
from django.urls import reverse
from rest_framework.test import APIClient

from feed.models import Post

# Create your tests here.

@pytest.fixture
def api_client():
   return APIClient()

@pytest.fixture
def create_user():
    def make_user():
        return User.objects.create_user(username=f'Younes{random.randint(0, 10000)}', email=f'younesdjelloul{random.randint(0, 10000)}@gmail.com', password='younes3334')
    return make_user

@pytest.fixture
def logged_api_client(
   db, create_user, api_client
):
   user = create_user()
   api_client.force_authenticate(user=user)
   yield api_client, user
   api_client.force_authenticate(user=None)

@pytest.mark.django_db
def test_user_and_profile_creation():
    user = User.objects.create_user(username='Younes', email='younesdjelloul14@gmail.com', password='younes3334')

    assert User.objects.first() == user
    assert Profile.objects.first().user == user


@pytest.mark.django_db
@pytest.mark.parametrize(
    'username, email, password1, password2, status_code', [
        ('', '', '', '', 400),
        ('', '', 'younes--44', 'younes--44', 400),
        ('Younes', '', '', 'younes--44', 400),
        ('', 'younes@younes.com', '', '', 400),
        ('Younes', 'younes@younes.com', '', '', 400),
        ('Younes', 'younes@younes.com', 'younes--22', 'passowrdsNotMatch', 400),
        ('Younes', 'younes@younes.com', 'younes--44', 'younes--44', 201)
    ]
)
def test_user_registration(username, email, password1, password2, status_code, api_client):
    url = reverse('accounts')
    data = {
        'username': username,
        'email': email,
        'password1': password1,
        'password2': password2
    }

    response = api_client.post(url, data)

    assert response.status_code == status_code
    if status_code == 201: assert User.objects.first().username == username

@pytest.mark.django_db
def test_retreive_all_users(api_client):
    url = reverse('accounts')

    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.data) == len(User.objects.all())

@pytest.mark.django_db
def test_get_one_user_instance(logged_api_client):
    client, user = logged_api_client

    url = reverse('account_detail')

    response = client.get(url)
    assert response.status_code == 200
    assert response.json()['username'] == user.username

@pytest.mark.django_db
def test_update_one_user_instance(logged_api_client):
    client, user = logged_api_client
    url = reverse('account_detail')

    data = {
        'username': 'AnotherYounes'
    }

    response = client.patch(url, data)
    assert response.status_code == 200
    assert user.username == 'AnotherYounes'

@pytest.mark.django_db
def test_delete_one_user_instance(logged_api_client):
    client, user = logged_api_client
    url = reverse('account_detail')

    response = client.delete(url)
    assert response.status_code == 200
    assert len(User.objects.all()) == 0

@pytest.mark.django_db
def test_get_user_profile(api_client):
    user = User.objects.create_user(username='Younes', email='younes@younes.com', password='password--44')
    url  = reverse('profile_detail', args=[user.profile.id])

    response = api_client.get(url)
    assert response.status_code == 200
    assert response.json()['fullname'] == user.username


@pytest.mark.parametrize(
    'profile_id, fullname, status_code', [
        (0, '', 404),
        (1, '', 400),
        (1, 'YounesNewName', 200),
    ]
)
@pytest.mark.django_db
def test_update_user_profile(profile_id, fullname, status_code, api_client):
    user = User.objects.create_user(username='Younes', email='younes@younes.com', password='password--44')
    url  = reverse('profile_detail', args=[profile_id])

    data = {
        'fullname': fullname
    }

    response = api_client.patch(url, data)
    assert response.status_code == status_code

    if response.status_code == 200:
        assert response.json()['fullname'] == fullname

@pytest.mark.parametrize(
    'profile_id, status_code', [
        (0, 404),
        (1, 200),
    ]
)
@pytest.mark.django_db
def test_delete_user_profile(profile_id, status_code, api_client):
    User.objects.create_user(username='Younes', email='younes@younes.com', password='password--44')
    
    url  = reverse('profile_detail', args=[profile_id])

    response = api_client.delete(url)
    assert response.status_code == status_code

    if response.status_code == 200:
        assert len(Profile.objects.all()) == 0


@pytest.mark.parametrize(
    'post_id, status_code', [
        (0, 404),
        (1, 201),
    ]
)
@pytest.mark.django_db
def test_create_profile_like(post_id, status_code, logged_api_client):
    client, user = logged_api_client
    Post.objects.create(profile=user.profile, caption='This is caption')

    url  = reverse('likes')

    data = {
        'post': post_id
    }

    response = client.post(url, data)
    assert response.status_code == status_code
    if response.status_code == 200:
        assert len(Like.objects.all()) == 1

@pytest.mark.django_db
def test_get_all_profile_likes(logged_api_client):
    client, user = logged_api_client
    post = Post.objects.create(profile=user.profile, caption='This is caption')

    Like.objects.create(profile=user.profile, post=post)

    url  = reverse('likes')

    response = client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 1

@pytest.mark.django_db
def test_get_one_profile_like(logged_api_client):
    client, user = logged_api_client
    post = Post.objects.create(profile=user.profile, caption='This is caption')

    like = Like.objects.create(profile=user.profile, post=post)

    url  = reverse('like_detail', args=[like.id])

    response = client.get(url)
    assert response.status_code == 200    
    assert response.json()['post'] == post.id

@pytest.mark.django_db
def test_get_one_profile_like(logged_api_client):
    client, user = logged_api_client
    post = Post.objects.create(profile=user.profile, caption='This is caption')

    like = Like.objects.create(profile=user.profile, post=post)

    url  = reverse('like_detail', args=[like.id])

    response = client.delete(url)
    assert response.status_code == 200    
    assert len(Like.objects.all()) == 0