from flask import Flask, send_from_directory, request, jsonify, redirect
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotify_utils import (
    get_playlist_tracks,
    extract_added_dates,
    generate_month_range,
    aggregate_by_season,
)
import logging
from collections import Counter

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, static_folder="../frontend/build")

token_info = None

# Predefined playlists
predefined_playlists = [
    {"id": os.getenv("RAPPERONI"), "name": "Rapperoni"},
    {"id": os.getenv("PENISLINE"), "name": "Penis Line"},
    {"id": os.getenv("PENIS69"), "name": "음경육십구"},
    {"id": os.getenv("HOMELESS"), "name": "Homeless"},
    {"id": os.getenv("YEAHMAN"), "name": "Yeah man"},
]

# Initialize SpotifyOAuth
sp_oauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope="playlist-read-private",
    cache_path=".cache",
)


@app.route("/")
def serve():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(app.static_folder, path)


@app.route("/api/login")
def login():
    auth_url = sp_oauth.get_authorize_url()
    return jsonify({"url": auth_url})


@app.route("/callback")
def callback():
    logging.info("Callback route accessed")
    try:
        logging.info(f"Callback received with args: {request.args}")

        code = request.args.get("code")
        global token_info
        token_info = sp_oauth.get_access_token(code)

        logging.info(f"Token info after get_token call: {token_info}")

        if not token_info or "access_token" not in token_info:
            return jsonify({"error": "Failed to get token_info"}), 500

        sp_oauth._save_token_info(token_info)

        return redirect("/")

    except Exception as e:
        logging.error(f"Error in callback: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/playlists")
def playlists():
    return jsonify(predefined_playlists)


@app.route("/api/predefined_playlists")
def predefined_playlists_route():
    return jsonify(predefined_playlists)


def get_token():
    global token_info
    token_info = sp_oauth.get_cached_token()

    if not token_info:
        return None

    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])

    return token_info


@app.route("/api/analyze", methods=["POST"])
def analyze():
    token_info = get_token()

    if not token_info or "access_token" not in token_info:
        return jsonify({"error": "No valid token_info available"}), 500

    sp = spotipy.Spotify(auth=token_info["access_token"])

    data = request.get_json()
    playlist_id = data.get("playlistId")
    view_mode = data.get("viewMode", "month")
    start = data.get("start", "2022-09" if view_mode == "month" else "Fall 2022")

    logging.info(
        f"Received playlistId: {playlist_id}, viewMode: {view_mode}, start: {start}"
    )
    logging.info(f"Current token_info: {token_info}")

    if not playlist_id:
        return jsonify({"error": "No playlist ID provided"}), 400

    try:
        tracks = get_playlist_tracks(sp, playlist_id)
        added_dates = extract_added_dates(tracks)

        if not added_dates:
            return jsonify({"labels": [], "data": []})

        if view_mode == "season":
            labels, data = aggregate_by_season(added_dates, start)
        else:
            added_months = [date[:7] for date in added_dates]
            month_counts = Counter(added_months)
            sorted_months = sorted(month_counts.items())

            start_month = sorted_months[0][0] if start == "start" else start
            end_month = sorted_months[-1][0]
            all_months = generate_month_range(start_month, end_month)

            labels = all_months
            data = [month_counts.get(month, 0) for month in all_months]

        return jsonify({"labels": labels, "data": data})

    except ValueError as ve:
        logging.error(f"ValueError during analysis: {ve}")
        return jsonify({"error": str(ve)}), 500
    except Exception as e:
        logging.error(f"Error during analysis: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/logout")
def logout():
    try:
        # Clear the cached token
        os.remove(".cache")
        global token_info
        token_info = None
        return jsonify({"message": "Logged out successfully"}), 200
    except Exception as e:
        logging.error(f"Error during logout: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(port=8888)
