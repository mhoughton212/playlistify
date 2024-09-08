import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import request
import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Get environment variables
client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")
scope = "playlist-read-private"

# Disable caching by setting cache_path to None
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
)
