import csv
import json
import random

from consts import DATA_DIR 


# Load all possible ids in the universe for tracks/albums/artists 
def read_universe_from_csv(type):
    if type == 'artists':
        csvfile = 'all_artists.csv'
    elif type == 'albums':
        csvfile = 'all_albums.csv'
    elif type == 'tracks':
        csvfile = 'all_tracks.csv'

    with open(csvfile, mode='r', encoding='UTF8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        all_ids = list(reader)[0]
        return all_ids


# Fetch a track id present in a given playlist
def get_positive_track(playlist_track_ids):
    idx = random.randint(0, len(playlist_track_ids) - 1)
    track = playlist_track_ids[idx]
    return track

# Fetch a track id not present in a given playlist
def get_negative_track(playlist_track_ids, all_track_ids):
    idx = random.randint(0, len(all_track_ids) - 1)    
    track = all_track_ids[idx]
    while track in playlist_track_ids + consts.blacklisted_track_ids:
        idx = random.randint(0, len(all_track_ids) - 1)    
        track = all_track_ids[idx]

    return track

def build_track_feature_dict():
    track_feature_dict = {}

    with open('tracks_data.csv', newline='', encoding='UTF8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            track_feature_dict[row['track_id']] = row

        csvfile.close()

    return track_feature_dict

def read_ids_from_csv(csv_file_path):
    ids = []
    try:
        with open(csv_file_path, 'r') as csvfile:
            # Read all the IDs from the single line
            content = csvfile.read()
            ids = content.split(',')
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    
    return ids

def get_tracks_from_playlist_id(pid):
    track_ids = []

    lower = 1000 * (pid // 1000)
    upper = lower + 999
    
    with open(f"{DATA_DIR}/mpd.slice.{lower}-{upper}.json") as f:
        json_data = json.load(f)
        for playlist in json_data['playlists']:
            if playlist['pid'] == pid:
                for track in playlist['tracks']:
                    track_id = track['track_uri'].split(":")[2]
                    track_ids.append(track_id)

    return track_ids