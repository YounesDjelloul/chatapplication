from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Post)
admin.site.register(PostComment)
admin.site.register(Story)
admin.site.register(StoryView)
admin.site.register(PostMedia)