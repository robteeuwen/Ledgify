from datetime import datetime

import pandas as pd
import requests
from flask import Flask, redirect, url_for, g, session, request, render_template
from authlib.integrations.requests_client import OAuth2Session
import os

"""
Application Factory for the main app

Resources: 
https://docs.authlib.org/en/latest/client/requests.html
"""

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY')

    with app.app_context():
        @app.route('/')
        def index():
            if session.get('token'):
                if token_expired():
                    token_refresh()

                token = session.get('token')

                # get user's profile info (for displaying the name)
                url = 'https://api.spotify.com/v1/me'
                headers = {
                    'Authorization': 'Bearer ' + token['access_token']
                }
                result = requests.get(url, headers=headers)
                user = result.json()

                # get recently played tracks
                url = 'https://api.spotify.com/v1/me/player/recently-played'
                params = {'limit': 50}
                result = requests.get(url, headers=headers, params=params)
                content = result.json()
                if content.get('items'):
                    played_tracks = content['items']

                # put in a dataframe
                data = {
                    'track_name': [track['track']['name'] for track in played_tracks],
                    'artist_name': [track['track']['artists'][0]['name'] for track in played_tracks],
                    'played_at': [track['played_at'] for track in played_tracks],
                    'playlist_uri': [track['context']['href'] for track in played_tracks],
                    'refreshed_count': 0
                }

                df = pd.DataFrame(data)
                df.played_at = pd.to_datetime(df.played_at)\
                    .dt.tz_convert('Europe/Amsterdam')\
                    .dt.strftime('%m/%d/%Y, %H:%M:%S')

                # get playlist information by creating a list of unique playlist uri's and querying them one by one
                # then merge the resulting dataframe of playlist names to the original dataframe
                playlists = pd.unique(df['playlist_uri'])
                names = [requests.get(playlist, headers=headers).json()['name'] for playlist in playlists]
                data = {
                    'playlist_uri': playlists,
                    'playlist_name': names
                }
                playlist_names = pd.DataFrame(data)

                df = df.merge(playlist_names, how='left', on='playlist_uri')

                # make a dict for easier looping in the template
                tracks = df.to_dict('records')
                tracks_json = df.to_json(orient='records')

                return render_template('index.html', name=user['display_name'], played_tracks=tracks,
                                       tracks_json=tracks_json)
            return "<p>Hello World!</p>"

        @app.route('/login')
        def spotify_login():
            token_endpoint = 'https://accounts.spotify.com/authorize'
            client_id = os.getenv('SPOTIFY_CLIENT_ID')
            client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
            redirect_url = url_for('authorize', _external=True)

            s = OAuth2Session(
                client_id, client_secret,
                scope='user-read-recently-played',
                redirect_uri=redirect_url
            )
            auth_url = s.create_authorization_url(token_endpoint)
            url = auth_url[0]
            state = auth_url[1]
            session['state'] = state

            return redirect(url)

        @app.route('/authorize')
        def authorize():
            state = session.get('state')
            client_id = os.getenv('SPOTIFY_CLIENT_ID')
            client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
            token_endpoint = 'https://accounts.spotify.com/api/token'
            authorization_response = request.url
            redirect_url = url_for('authorize', _external=True)

            s = OAuth2Session(
                client_id, client_secret,
                scope='user-read-recently-played',
                state=state,
                redirect_uri=redirect_url
            )
            token = s.fetch_token(token_endpoint,authorization_response=authorization_response)
            session['token'] = token

            return redirect(url_for('index'))

        def token_refresh():
            token = session.get('token')
            refresh_token = token['refresh_token']
            client_id = os.getenv('SPOTIFY_CLIENT_ID')
            client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
            token_endpoint = 'https://accounts.spotify.com/api/token'
            redirect_url = url_for('authorize', _external=True)

            s = OAuth2Session(
                client_id, client_secret,
                scope='user-read-recently-played',
                redirect_uri=redirect_url
            )
            token = s.refresh_token(token_endpoint, refresh_token)

            session['token'] = token

        def token_expired():
            token = session.get('token')
            expires = datetime.fromtimestamp(token['expires_at'])
            now = datetime.now()
            if expires < now:
                return True
            else:
                return False

    return app