from django.db import models
from django.core.exceptions import ObjectDoesNotExist

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

class GeneralManager(models.Manager):
    def safe_get(self, **kwargs):
        try:
            return self.get(**kwargs)
        except ObjectDoesNotExist:
            return None

class UserManager(BaseUserManager):
	def create_user(self, username, email, password, **kwargs):
		if email and username and password:
			user = User(email=email, username=username)
			user.set_password(password)
			user.save()

			return user

	def create_superuser(self, username, email, password):
		if email and username and password:
			user = User(username=username, email=email, is_superuser=True, is_staff=True)
			user.set_password(password)
			user.save()

			return user

class User(AbstractUser):
    first_name = None
    last_name  = None

    username = models.CharField(max_length=40, unique=True)
    id       = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    email    = models.EmailField(unique=True)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username']
    objects         = UserManager()

    def __str__(self):
	    return self.username
    
class Profile(models.Model):

    gender_choices = [
        ('M', 'male'),
	    ('F', 'female')
    ]
    
    user     = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=40)
    bio      = models.TextField(default="", max_length=60)
    gender   = models.CharField(choices=gender_choices, max_length=2, null=True, blank=True)
    picture  = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    objects  = GeneralManager()

    def __str__(self) -> str:
        return self.fullname
    
@receiver(post_save, sender=User)
def create_profile(created, instance, **kwargs):
    if created:
        Profile.objects.create(user=instance, fullname=instance.username)

class Like(models.Model):
	
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    post = models.ForeignKey("feed.Post", on_delete=models.CASCADE)

    objects = GeneralManager()

    def __str__(self):
	    return str(self.profile)