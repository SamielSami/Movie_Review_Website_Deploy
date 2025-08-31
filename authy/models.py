from django.db import models
from django.contrib.auth.models import User
from movie.models import Movie

from django.db.models.signals import post_save

from PIL import Image
from django.conf import settings
import os

# Create your models here.

def user_directory_path(instance, filename):
	profile_pic_name = 'user_{0}/profile.jpg'.format(instance.user.id)
	full_path = os.path.join(settings.MEDIA_ROOT, profile_pic_name)

	if os.path.exists(full_path):
		os.remove(full_path)
	return profile_pic_name


class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
	first_name = models.CharField(max_length=50, null=True, blank=True)
	last_name = models.CharField(max_length=50, null=True, blank=True)
	location = models.CharField(max_length=50, null=True, blank=True)
	url = models.CharField(max_length=80, null=True, blank=True)
	profile_info = models.TextField(max_length=150, null=True, blank=True)
	created = models.DateField(auto_now_add=True)
	to_watch = models.ManyToManyField(Movie, related_name='towatch')
	watched = models.ManyToManyField(Movie, related_name='watched')
	picture = models.ImageField(upload_to=user_directory_path, blank=True, null=True)

	def save(self, *args, **kwargs):
		super().save(*args, **kwargs)
		SIZE = 250, 250

		if self.picture:
			pic = Image.open(self.picture.path)
			pic.thumbnail(SIZE, Image.LANCZOS)
			pic.save(self.picture.path)

	def __str__(self):
		return self.user.username


class PersonalList(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='personal_lists')
	name = models.CharField(max_length=60)
	movies = models.ManyToManyField(Movie, related_name='in_personal_lists', blank=True)
	is_private = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = [('user', 'name')]
		ordering = ['-created_at']

	def __str__(self):
		return f"{self.name} (@{self.user.username})"

	@property
	def items_count(self):
		return self.movies.count()


def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)


def save_user_profile(sender, instance, **kwargs):
	instance.profile.save()


post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)
