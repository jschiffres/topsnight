from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.contrib.auth.models import User
from .models import Playlist, TopsGroup

class CreateUserForm(UserCreationForm):
	email = forms.EmailField(required=True)
	class Meta:
		model = User
		fields = ['username', 'email', 'password1', 'password2']

class PlaylistForm(ModelForm):
	class Meta:
		model = Playlist
		fields = ['name', 'url']


class TopsGroupForm(ModelForm):
	class Meta:
		model = TopsGroup
		fields = ['name', 'password', 'min_date', 'max_date', 'playlistlength']