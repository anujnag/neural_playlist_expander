import csv
import json
import random
import requests
import sys
import time

import consts

csv.field_size_limit(sys.maxsize)

# ID and Secret masked for security reasons
client_id = 'CLIENT-ID'
client_secret = 'CLIENT-SECRET'

def write_data_to_csv(data_dict, type):
    csv_filename = type + '_data.csv'
    
    if type == 'artists':
        fieldnames = consts.artist_fieldnames
    elif type == 'tracks':
        fieldnames = consts.track_fieldnames
    elif type == 'albums':
        fieldnames = consts.album_fieldnames
    elif type == 'playlists':
        fieldnames = consts.playlist_fieldnames        
    
    with open(csv_filename, 'w', newline='', encoding='UTF8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(data_dict)
        csvfile.close()    

def append_data_to_csv(data_dict, type):
    csv_filename = type + '_data.csv'
    
    if type == 'artists':
        fieldnames = consts.artist_fieldnames
    elif type == 'tracks':
        fieldnames = consts.track_fieldnames
    elif type == 'albums':
        fieldnames = consts.album_fieldnames    
    elif type == 'playlists':
        fieldnames = consts.playlist_fieldnames         
    
    with open(csv_filename, 'a', newline='', encoding='UTF8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(data_dict)
        csvfile.close() 

def load_ids_from_csv(type):
    csv_filename = type + '_data.csv'
    id_set = set()

    if type == 'artists':
        fieldnames = consts.artist_fieldnames
    elif type == 'tracks':
        fieldnames = consts.track_fieldnames
    elif type == 'albums':
        fieldnames = consts.album_fieldnames    
    elif type == 'playlists':
        fieldnames = consts.playlist_fieldnames        

    with open(csv_filename, newline='', encoding='UTF8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            id_set.add(row[fieldnames[0]])

        csvfile.close()

    return id_set        

# Fetch all preprocessed track data
def get_processed_tracks():
    track_dict = {}

    with open('tracks_data.csv', newline='', encoding='UTF8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            track_dict[row['track_id']] = {
                'artist': row['track_artists'].strip('][').replace("\'", "").split(", "),
                'album': row['track_album']
            }

        csvfile.close()    

    return track_dict

# Fetch all preprocessed artist data
def get_processed_artists():
    artist_dict = {}

    with open('artists_data.csv', newline='', encoding='UTF8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            artist_dict[row['artist_id']] = {
                'top_tracks': row['artist_top_tracks'].strip('][').replace("\'", "").split(", "),
                'related_artists': row['related_artists'].strip('][').replace("\'", "").split(", ")
            }

        csvfile.close()    

    return artist_dict

# Fetch all preprocessed album data
def get_processed_albums():
    album_dict = {}

    with open('albums_data.csv', newline='', encoding='UTF8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            album_dict[row['album_id']] = {
                'tracks': row['album_tracks'].strip('][').replace("\'", "").split(", ")
            }

        csvfile.close()

    return album_dict    

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

# Refresh API access token on expiry
def refresh_access_token():
    print('Refreshing Access Token')
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post('https://accounts.spotify.com/api/token', data=data, headers=headers)
    response_dict = json.loads(response.text)
    token_type, access_token = response_dict['token_type'], response_dict['access_token']
    print(f'New Token: {access_token}')
    return token_type, access_token

def retry_http_call(response, request_url, headers):
    if response.status_code == 401: # Access token expired
        token_type, access_token = refresh_access_token()
        auth_payload = token_type + '  ' + access_token
        headers = {
            'Authorization': auth_payload,
        }
        response = requests.get(request_url, headers=headers)
    elif response.status_code == 429: # Rate limit exceeded
        print(response.headers)
        retry_after_secs = int(response.headers['retry-after']) + 1
        print('Rate Limit Exceeded, sleeping for ' + str(retry_after_secs) + ' seconds')
        time.sleep(retry_after_secs)
        response = requests.get(request_url, headers=headers)
    elif response.status_code == 504 or response.status_code == 404: # Bad request response
        print('Response status code is ' + str(response.status_code) + ', sleeping for 15 seconds')
        print(request_url)
        time.sleep(15)
        response = requests.get(request_url, headers=headers)
    else:
        print(response.text)
        print(request_url)
        print('Response status code not recognized: ' + str(response.status_code))

    return response, headers

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

def update_track_feature_dict(track_feature_dict, new_tracks):
    return track_feature_dict