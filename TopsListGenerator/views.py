from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from .forms import CreateUserForm, PlaylistForm, TopsGroupForm
from .models import Playlist, TopsGroup
from django.db import IntegrityError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from.functions import DFtoHTML, URLtoDF, AggregateTopsList
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd



def home(request):
    return render(request, 'TopsListGenerator/home.html')

'''AUTHENTICATION: Sign-up, Login, Logout'''

def signupuser(request):
    if request.method == "GET":
        return render(request, 'TopsListGenerator/signupuser.html', {'form':CreateUserForm()})
    else:
        if request.POST.get('password1') == request.POST.get('password2'):
            try:
                if User.objects.filter(email=request.POST.get('email')).exists():
                    return render(request, 'TopsListGenerator/signupuser.html', {'form':CreateUserForm(), 'error':'Email provided is already associated with an account.'})
                else:
                    user = User.objects.create_user(username=request.POST.get('username'), email=request.POST.get('email'), password=request.POST.get('password1')) 
                    user.save()
                    login(request, user)
                    messages.success(request, "User created successfully!")
                    return redirect('userplaylists')
            except IntegrityError: 
                return render(request, 'TopsListGenerator/signupuser.html', {'form':CreateUserForm(), 'error':'Username has already been taken.'})
        else:
            return render(request, 'TopsListGenerator/signupuser.html', {'form':CreateUserForm(), 'error':'Passwords did not match.'})

def loginuser(request):
    if request.method == "GET":
        return render(request, 'TopsListGenerator/loginuser.html', {'form':AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user is None:
            return render(request, 'TopsListGenerator/loginuser.html', {'form':AuthenticationForm(), 'error':"Username and password did not match."})
        else:
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect('userplaylists')

@login_required
def logoutuser(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "Logged out successfully!")
        return redirect('home')

'''PLAYLISTS: User's Playlists, Import New Playlist, Edit Playlist, Delete Playlist, Refresh Playlist '''

@login_required
def userplaylists(request):
    playlists = Playlist.objects.filter(user=request.user)
    return render(request, 'TopsListGenerator/userplaylists.html', {'playlists' : playlists})

@login_required
def importplaylist(request):
    if request.method == "GET":
        return render(request, 'TopsListGenerator/importplaylist.html', {'form': PlaylistForm()})
    else:
        try:
            form = PlaylistForm(request.POST)
            newplaylist = form.save(commit=False)
            newplaylist.user = request.user
            ''' Spotify API Logic '''
            playlistDF = URLtoDF(form['url'].value())
            newplaylist.playlistHTML = DFtoHTML(playlistDF)
            newplaylist.songs = len(playlistDF)
            newplaylist.save()
            messages.success(request, f"{newplaylist.name} imported successfully!")
            return redirect('userplaylists')
        except (spotipy.SpotifyException, ValueError):
            return render(request, 'TopsListGenerator/importplaylist.html', {'form':PlaylistForm(), 'error': 'Sptofiy playlist URL not recongnized, please try again.'})

@login_required
def editplaylist(request, playlist_pk):
    playlist = get_object_or_404(Playlist, pk=playlist_pk, user=request.user)
    if request.method == "GET":
        form = PlaylistForm(instance=playlist)
        return render(request, 'TopsListGenerator/editplaylist.html', {'playlist' : playlist, 'form' : form})
    else:
        try:
            form = PlaylistForm(request.POST, instance=playlist)
            editedplaylist = form.save(commit=False)
            editedplaylist.user = request.user
            ''' Spotify API Logic '''
            playlistDF = URLtoDF(form['url'].value())
            editedplaylist.playlistHTML = DFtoHTML(playlistDF)
            editedplaylist.songs = len(playlistDF)
            editedplaylist.save()
            messages.success(request, f"{editedplaylist.name} info updated successfully!")
            return redirect('userplaylists')
        except (spotipy.SpotifyException, ValueError):
            return render(request, 'TopsListGenerator/editplaylist.html', {'playlist' : playlist, 'form' : form,'error' : 'Sptofiy playlist URL not recongnized, please try again.'})

@login_required
def deleteplaylist(request, playlist_pk):
    playlist = get_object_or_404(Playlist, pk=playlist_pk, user=request.user) 
    if request.method == "POST":
        playlist.delete()
        messages.success(request, f"{playlist.name} deleted successfully!")
        return redirect('userplaylists')

@login_required
def refreshplaylist(request, playlist_pk):
    refreshedplaylist = get_object_or_404(Playlist, pk=playlist_pk, user=request.user)
    playlist_url = refreshedplaylist.url

    if request.method == "POST":
        playlistDF = URLtoDF(playlist_url)
        refreshedplaylist.playlistHTML = DFtoHTML(playlistDF)
        refreshedplaylist.songs = len(playlistDF)
        refreshedplaylist.save()
        messages.success(request, f"{refreshedplaylist.name} data refreshed successfully!")
        return redirect('userplaylists')

def removegroupfromplaylist(request, playlist_pk):
    playlist = get_object_or_404(Playlist, pk=playlist_pk, user=request.user)
    group = get_object_or_404(TopsGroup, pk=request.POST.get('group'))
    form = PlaylistForm(instance=playlist)
    if request.method == "POST":
        playlist.groups.remove(request.POST.get('group'))
        messages.success(request, f"{playlist.name} removed from {group.name} successfully!")
        return redirect('userplaylists')

'''GROUPS: User's Group, Create New Group, All Existing Groups, Edit Group, Delete Group, View Group'''

@login_required
def usergroups(request):
    groups = TopsGroup.objects.filter(user=request.user)
    return render(request, 'TopsListGenerator/usergroups.html', {'groups' : groups})

@login_required
def creategroup(request):
    if request.method == "GET":
        return render(request, 'TopsListGenerator/creategroup.html', {'form': TopsGroupForm()})
    else:
        if request.POST.get('password') == request.POST.get('password2') and request.POST.get('min_date') < request.POST.get('max_date'):
            form = TopsGroupForm(request.POST)
            newgroup = form.save(commit=False)
            newgroup.password = form['password'].value()
            newgroup.user = request.user
            newgroup.save()
            messages.success(request, f"{newgroup.name} created successfully!")
            return redirect('usergroups')
        elif request.POST.get('password') != request.POST.get('password2'):
            return render(request, 'TopsListGenerator/creategroup.html', {'form':TopsGroupForm(), 'error':'Passwords did not match.'})
        else:
            return render(request, 'TopsListGenerator/creategroup.html', {'form':TopsGroupForm(), 'error':'Minimum Release Date must be before Maximum Release Date.'})

def allgroups(request):
    groups = TopsGroup.objects.all()
    return render(request, 'TopsListGenerator/allgroups.html', {'groups' : groups})

@login_required
def editgroup(request, group_pk):
    group = get_object_or_404(TopsGroup, pk=group_pk, user=request.user)
    form = TopsGroupForm(instance=group)
    playlists = Playlist.objects.filter(groups=group_pk)
    if request.method == "GET":
        return render(request, 'TopsListGenerator/editgroup.html', {'group' : group, 'playlists' : playlists, 'form' : form})
    else:
        if request.POST.get('password') == request.POST.get('password2') and request.POST.get('min_date') < request.POST.get('max_date'):
            form = TopsGroupForm(request.POST, instance=group)
            editedgroup = form.save(commit=False)
            editedgroup.password = form['password'].value()
            editedgroup.user = request.user
            editedgroup.save()
            messages.success(request, f"{editedgroup.name} info updated successfully!")
            return redirect('usergroups')
        elif request.POST.get('password') != request.POST.get('password2'):
            return render(request, 'TopsListGenerator/editgroup.html', {'group' : group, 'playlists' : playlists, 'form' : form, 'error':'Passwords did not match.'})
        else:
            return render(request, 'TopsListGenerator/editgroup.html', {'group' : group, 'playlists' : playlists, 'form' : form, 'error':'Minimum Release Date must be before Maximum Release Date.'})

@login_required
def removeplaylistfromgroup(request, group_pk):
    playlist = get_object_or_404(Playlist, pk=request.POST.get('playlist'))
    group = get_object_or_404(TopsGroup, pk=group_pk, user=request.user)
    form = PlaylistForm(instance=playlist)
    if request.method == "POST":
        playlist.groups.remove(group_pk)
        messages.success(request, f"{playlist.name} removed from {group.name} successfully!")
        return redirect('usergroups')

@login_required
def deletegroup(request, group_pk):
    group = get_object_or_404(TopsGroup, pk=group_pk, user=request.user)

    if request.method == "POST":
        group.delete()
        messages.success(request, f"{group.name} deleted successfully!")
        return redirect('usergroups')

def viewgroup(request, group_pk):
    if request.user.is_authenticated:
        group = get_object_or_404(TopsGroup, pk=group_pk)
        playlists = Playlist.objects.filter(user=request.user).exclude(groups=group)
        group_playlists = Playlist.objects.filter(groups=group_pk)
        if request.method == "GET":
            return render(request, 'TopsListGenerator/viewgroup.html', {'group' : group, 'playlists' : playlists, 'group_playlists' : group_playlists})
        else:
            if request.POST.get('password') == group.password:
                playlist = get_object_or_404(Playlist, pk=request.POST.get('playlist'))
                playlist.groups.add(group)
                messages.success(request, f"{playlist.name} added to {group.name} successfully!")
                return render(request, 'TopsListGenerator/viewgroup.html', {'group' : group, 'playlists' : playlists, 'group_playlists' : group_playlists})
            else:
                return render(request, 'TopsListGenerator/viewgroup.html', {'group' : group, 'playlists' : playlists, 'group_playlists' : group_playlists, 'error' : 'Incorrect Password'})
    else:
       group = get_object_or_404(TopsGroup, pk=group_pk)
       group_playlists = Playlist.objects.filter(groups=group_pk)
       return render(request, 'TopsListGenerator/viewgroup.html', {'group' : group, 'group_playlists' : group_playlists})

@login_required
def aggregategroup(request, group_pk):
    agggroup = get_object_or_404(TopsGroup, pk=group_pk, user=request.user)
    aggplaylists = Playlist.objects.filter(groups=agggroup)
    song_limit = int(request.POST.get('playlistlength'))
    spotify_user_id = request.POST.get('spotify_user_id')
    start_date = request.POST.get('min_date')
    end_date = request.POST.get('max_date')

    if request.POST.get('min_date') < request.POST.get('max_date'):
        try:
            topslist = AggregateTopsList(agggroup, aggplaylists, song_limit, spotify_user_id, start_date, end_date)
            if len(topslist)==2:
                agggroup.playlistHTML = DFtoHTML(topslist[0])
                agggroup.save()
                messages.success(request, f"{agggroup.name} Topslist created successfully!")
                return render(request, 'TopsListGenerator/aggregategroup.html', {'group' : agggroup, 'playlist_url' : topslist[1]})
            else:
                group = agggroup
                playlists = Playlist.objects.filter(user=request.user).exclude(groups=group)
                group_playlists = Playlist.objects.filter(groups=group_pk)
                return redirect(request, 'TopsListGenerator/viewgroup.html', {'group' : group, 'playlists' : playlists, 'group_playlists' : group_playlists, 'error' : 'Release Date Range yields no results'})

        except spotipy.SpotifyException:
            group = get_object_or_404(TopsGroup, pk=group_pk)
            playlists = Playlist.objects.filter(user=request.user).exclude(groups=group)
            group_playlists = Playlist.objects.filter(groups=group_pk)
            return render(request, 'TopsListGenerator/viewgroup.html', {'group' : group, 'playlists' : playlists, 'group_playlists' : group_playlists, 'error' : 'Playlist aggregation failed, please review potify Username'})
    else:
        group = get_object_or_404(TopsGroup, pk=group_pk)
        playlists = Playlist.objects.filter(user=request.user).exclude(groups=group)
        group_playlists = Playlist.objects.filter(groups=group_pk)
        return render(request, 'TopsListGenerator/viewgroup.html', {'group' : group, 'playlists' : playlists, 'group_playlists' : group_playlists, 'error' : 'Minimum Release Date must be before Maximum Release Date.'})

'''Other'''
def FAQs(request):
    return render(request, 'TopsListGenerator/FAQs.html')

def about(request):
    return render(request, 'TopsListGenerator/about.html')
