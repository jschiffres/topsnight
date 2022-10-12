from django.db import models
from django.contrib.auth.models import User

class TopsGroup(models.Model):
	name = models.CharField(max_length=100)
	password = models.CharField(max_length=100)
	playlistHTML = models.TextField(blank=True,null=True)
	created = models.DateTimeField(auto_now_add=True)
	playlistlength = models.IntegerField(blank=True,null=True)
	min_date = models.DateField(blank=True,null=True)
	max_date = models.DateField(blank=True,null=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE)

	def __str__(self):
		return self.name

class Playlist(models.Model):
	name = models.CharField(max_length=100)
	url = models.URLField()
	songs = models.IntegerField(blank=True,null=True)
	playlistHTML = models.TextField(blank=True,null=True)
	created = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	groups = models.ManyToManyField(TopsGroup)

	def __str__(self):
		return self.name