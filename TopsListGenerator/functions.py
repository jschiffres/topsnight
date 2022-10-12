from django.conf import settings
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd

def DFtoHTML(df):
	HTMLdf = df.to_html()
	edit1 = HTMLdf.replace('dataframe','table table-striped table-hover')
	edit2 = edit1.replace('thead','thead class="table-dark"')
	final = edit2.replace('tr style="text-align: right;"','tr style="text-align: center;"')
	return final

def URLtoDF(playlist_url):
	'''playlist_url = form['url'].value()'''
	spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
	results = spotify.playlist_items(playlist_url)
	tops = {}
	row = 1
	song_details = []
	points = len(results['items'])
	for song in results['items'][0:len(results['items'])]:
	    song_details.append(song['track']['artists'][0]['name'])
	    song_details.append(song['track']['name'])
	    song_details.append(song['track']['album']['release_date'])
	    tops[row]=song_details
	    song_details = []
	    points -= 1
	    row += 1
	playlistDF = pd.DataFrame.from_dict(tops, orient='index', columns=['Artist','Track','Released'])
	playlistDFclean = playlistDF.drop_duplicates(subset = ['Artist', 'Track'],keep ='first',ignore_index=True)
	playlistDFclean.insert(3,'Points',range(len(playlistDFclean),0,-1))
	playlistDFclean.index += 1
	return playlistDFclean

def AggregateTopsList(group,queryset,song_limit,spotify_user_id,start_date, end_date):

	scope="playlist-modify-public"

	'''Spotify API Authentication'''
	spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
	sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

	'''Song Details Variables'''
	tops = {}
	row = 1
	song_details = []
	points = song_limit
	
	'''urls = list of urls from queryset & playlistDF = list of DFs for each playlist'''
	urls = []
	playlistDF = []

	'''From the queryset put all urls into the url list'''
	for playlist in queryset:
	    urls.append(playlist.url)

	'''Loop through each playlist via their url and create a DF of their songs/details'''
	for url in urls:
	    results = spotify.playlist_items(url)
	    '''Loop through each song in a playlist to extract their details into song_details list'''
	    for song in results['items'][0:len(results['items'])]:
	        song_details.append(song['track']['artists'][0]['name'])
	        song_details.append(song['track']['name'])
	        song_details.append(song['track']['id'])
	        song_details.append(song['track']['album']['release_date'])
	        '''Add song_details list to tops dictionary'''
	        tops[row]=song_details
	        '''Reset song_details list for next song, add 1 to row variable to move to next index in tops dict'''
	        song_details = []
	        row += 1
	    '''Create DF from dictionary of songs,'''
	    playlist = pd.DataFrame.from_dict(tops, orient='index', columns=['Artist','Track','track_id','Released'])
	    '''remove duplicates'''
	    playlistclean = playlist.drop_duplicates(subset = ['Artist', 'Track'],keep ='first',ignore_index=True)
	    '''filter out songs not released within data range specified by user'''
	    playlistclean = playlistclean[(playlistclean['Released'] > start_date) & (playlistclean['Released'] < end_date)]
	    '''insert points column'''
	    playlistclean.insert(3,'Points',range(song_limit,song_limit-len(playlistclean),-1))
	    '''reset index'''
	    playlistclean.index += 1
	    '''trim cleaned playlist down to song_limit specified by user'''
	    playlistclean = playlistclean.head(song_limit)
	    '''Append the DF to the playlistDF list once each song has been iterated through and playlist has been cleaned'''
	    playlistDF.append(playlistclean)
	    '''Reset variables for next playlist'''
	    row = 1
	    tops = {}
	'''Append all the DFs in playlistDF on top of each other'''
	combined = pd.concat(playlistDF)
	'''Aggregate/group them by summing their points based on Artist/Track'''
	if len(combined)>0:
		grouped = combined.groupby(['Artist','Track'], as_index=False).agg({'track_id': 'first', 'Released': 'first', 'Points': 'sum'})
		'''Sort grouped DF and reset index'''
		sort = grouped.sort_values(by='Points', ascending=False, ignore_index=True)
		'''Reset index and trim playlist down to song_limit specified by user'''
		sort.index += 1
		trimmed = sort.head(song_limit)
		'''Create new DF based on the track_id column within the trimmed DF'''
		songs = trimmed['track_id']
		'''Drop the track_id from the trimmed DF'''
		trimmed.drop(columns=['track_id'], axis=1, inplace=True)
		'''Spotify API to create a new playlist, retrieve that playlist's ID and add all the songs within the songs DF'''
		createnewplaylist = sp.user_playlist_create(spotify_user_id, group.name, public=True, collaborative=False, description='test')
		newplaylistinfo = sp.user_playlists(spotify_user_id)
		playlist_id = newplaylistinfo['items'][0]['id']
		playlist_url = newplaylistinfo['items'][0]['external_urls']['spotify']
		add_tracks = sp.playlist_add_items(playlist_id, songs, position=None)
		'''Return trimmed DF for use in html template'''
		return [trimmed,playlist_url]
	else:
		return ['Release Date Range yields no results']

