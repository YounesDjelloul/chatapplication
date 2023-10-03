from django.db import models
import datetime
from accounts.models import GeneralManager

# Create your models here.

class Post(models.Model):
	profile = models.ForeignKey("accounts.Profile", on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now=True)
	caption = models.CharField(max_length=120)

	objects = GeneralManager()

	def toggle_like(self, profile):
		like_instance = PostLike.objects.safe_get(profile=profile)

		if like_instance:
			like_instance.delete()
			return 'Deleted'
		else:
			PostLike.objects.create(post=self, profile=profile)
			return 'Added'

	def is_profile_in_likes(self, profile):
		return PostLike.objects.filter(post=self, profile=profile).exists()

	def likes(self):
		return PostLike.objects.filter(post=self).count()

	def parent_comments(self):
		return PostComment.objects.filter(post=self, parent=None)

	def post_media(self):
		return PostMedia.objects.filter(post=self)

	def __str__(self):
		return f"Post by {self.profile}"

class PostLike(models.Model):
	profile = models.ForeignKey("accounts.Profile", on_delete=models.CASCADE)
	post = models.ForeignKey(Post, on_delete=models.CASCADE)

	objects = GeneralManager()

	def __str__(self):
		return f"Like by {self.profile} for {self.post}"

class PostComment(models.Model):
	profile = models.ForeignKey("accounts.Profile", on_delete=models.CASCADE)
	post = models.ForeignKey(Post, on_delete=models.CASCADE)
	parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now=True)
	content = models.TextField()
	is_deleted = models.BooleanField(default=False)

	objects = GeneralManager()

	def children(self):
		return PostComment.objects.filter(parent=self)

	def __str__(self):
		return f"Comment by {self.profile}"
	
class PostMedia(models.Model):
	post = models.ForeignKey(Post, on_delete=models.CASCADE)
	file = models.ImageField(upload_to='post_media/')

	def __str__(self):
		return f"media for {str(self.post)}"
	
class Story(models.Model):
	profile = models.ForeignKey("accounts.Profile", on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now=True)
	file = models.ImageField(upload_to='story_media/')
	expire_at = models.DateTimeField()

	def __str__(self):
		return f"Story by {self.profile}"
	
	def is_live(self):
		return datetime.datetime.now() < self.expire_at
	
class StoryView(models.Model):
	viewer = models.ForeignKey("accounts.profile", on_delete=models.CASCADE)
	story  = models.ForeignKey(Story, on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"{self.viewer} view {self.story}"