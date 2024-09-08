import logging
from collections import defaultdict
from datetime import datetime


def get_playlist_tracks(sp, playlist_id):
    try:
        results = sp.playlist_tracks(playlist_id)
        tracks = results["items"]
        while results["next"]:
            results = sp.next(results)
            tracks.extend(results["items"])
        return tracks
    except Exception as e:
        logging.error(f"Error fetching tracks: {e}")
        return []


def extract_added_dates(tracks):
    try:
        added_dates = [
            track["added_at"][:10] for track in tracks
        ]  # Extract "YYYY-MM-DD"
        return added_dates
    except Exception as e:
        logging.error(f"Error extracting added dates: {e}")
        return []


def generate_month_range(start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m")
    end = datetime.strptime(end_date, "%Y-%m")
    months = []

    while start <= end:
        months.append(start.strftime("%Y-%m"))
        if start.month == 12:
            start = start.replace(year=start.year + 1, month=1)
        else:
            start = start.replace(month=start.month + 1)

    return months


def month_to_season(year, month):
    month = int(month)
    if month in [12, 1, 2]:
        season_year = year if month != 12 else str(int(year) + 1)
        return f"Winter {season_year}"
    elif month in [3, 4, 5]:
        return f"Spring {year}"
    elif month in [6, 7, 8]:
        return f"Summer {year}"
    elif month in [9, 10, 11]:
        return f"Fall {year}"
    return None


def generate_season_range(start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m")
    end = datetime.strptime(end_date, "%Y-%m")
    seasons = []
    season_order = ["Winter", "Spring", "Summer", "Fall"]

    while start <= end:
        season = month_to_season(start.strftime("%Y"), start.strftime("%m"))
        if season not in seasons:
            seasons.append(season)
        next_month = start.month + 1
        if next_month == 13:
            next_month = 1
            start = start.replace(year=start.year + 1, month=next_month)
        else:
            start = start.replace(month=next_month)

    return seasons


def sort_seasons(season):
    season_order = {"Winter": 0, "Spring": 1, "Summer": 2, "Fall": 3}
    season_name, year = season.split()
    return (int(year), season_order[season_name])


def aggregate_by_season(added_dates, start_season="Fall 2022"):
    season_counts = defaultdict(int)
    for date in added_dates:
        try:
            year, month = date.split("-")[:2]
            season = month_to_season(year, month)
            if season:
                season_counts[season] += 1
        except ValueError as e:
            logging.error(f"Error processing date {date}: {e}")
            continue

    if not season_counts:
        return [], []

    sorted_dates = sorted(date.split("-")[:2] for date in added_dates)
    start_date = f"{sorted_dates[0][0]}-{sorted_dates[0][1]}"
    end_date = f"{sorted_dates[-1][0]}-{sorted_dates[-1][1]}"

    start_season_name, start_year = start_season.split(" ")
    season_order = ["Winter", "Spring", "Summer", "Fall"]

    # Ensure the start_season is in the correct format
    if start_season_name not in season_order:
        raise ValueError(f"Invalid start season: {start_season}")

    all_seasons = generate_season_range(start_date, end_date)
    all_seasons = [
        s
        for s in all_seasons
        if sort_seasons(s) >= (int(start_year), season_order.index(start_season_name))
    ]

    labels = all_seasons
    data = [season_counts.get(season, 0) for season in all_seasons]

    return labels, data
