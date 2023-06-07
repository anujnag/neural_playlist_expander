import csv
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
    elif type == 'playlists':
        fieldnames = consts.playlist_fieldnames        

    with open(csv_filename, newline='', encoding='UTF8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            id_set.add(row[fieldnames[0]])

    return id_set        

def read_universe_from_csv(type):
    if type == 'artists':
        csvfile = 'all_artists.csv'
    elif type == 'albums':
        csvfile = 'all_albums.csv'
    elif type == 'tracks':
        csvfile = 'all_tracks.csv'

    with open(csvfile, mode='r', encoding='UTF8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        all_artist_ids = list(reader)[0]
        return all_artist_ids

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
    if response.status_code == 401:
        token_type, access_token = refresh_access_token()
        auth_payload = token_type + '  ' + access_token
        headers = {
            'Authorization': auth_payload,
        }
        response = requests.get(request_url, headers=headers)
    elif response.status_code == 429:
        print(response.headers)
        retry_after_secs = int(response.headers['retry-after']) + 1
        print('Rate Limit Exceeded, sleeping for ' + str(retry_after_secs) + ' seconds')
        time.sleep(retry_after_secs)
        response = requests.get(request_url, headers=headers)
    elif response.status_code == 504 or response.status_code == 404:
        print('Response status code is ' + str(response.status_code) + ', sleeping for 15 seconds')
        print(request_url)
        time.sleep(15)
        response = requests.get(request_url, headers=headers)
    else:
        print(response.text)
        print(request_url)
        print('Response status code not recognized: ' + str(response.status_code))

    return response, headers

def get_positive_track(playlist_track_ids):
    idx = random.randint(0, len(playlist_track_ids) - 1)
    track = playlist_track_ids[idx]
    return track

def get_negative_track(playlist_track_ids, all_track_ids):
    idx = random.randint(0, len(all_track_ids) - 1)    
    track = all_track_ids[idx]
    while track in playlist_track_ids + consts.blacklisted_track_ids:
        idx = random.randint(0, len(all_track_ids) - 1)    
        track = all_track_ids[idx]

    return track

def generate_candidate_list(playlist):
    # code added in a private file to hide API keys and access tokens
    return generate_candidate_list(playlist)

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