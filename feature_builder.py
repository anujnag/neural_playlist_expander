import csv
import json
import requests

artist_fieldnames = ['artist_id', 'artist_name', 'artist_genres', 'artist_followers', 'artist_popularity', 'artist_type', 'artist_top_tracks', 'related_artists']
track_fieldnames = ['track_id']
client_id = 'CLIENT-ID' # Masked out entry, update while using
client_secret = 'CLIENT-SECRET' # Masked out entry, update while using

def write_data_to_csv(data_dicts, type):
    csv_filename = type + '_data.csv'
    
    if type == 'artist':
        fieldnames = artist_fieldnames
    elif type == 'track':
        fieldnames = track_fieldnames    
    
    with open(csv_filename, 'w', newline='', encoding='UTF8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        print(data_dicts)
        for dict in data_dicts:
            writer.writerow(dict)

        csvfile.close()    

def append_data_to_csv(data_dict, type):
    csv_filename = type + '_data.csv'
    
    if type == 'artists':
        fieldnames = artist_fieldnames
    
    with open(csv_filename, 'a', newline='', encoding='UTF8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(data_dict)
        csvfile.close() 

def load_ids_from_csv(type):
    csv_filename = type + '_data.csv'
    id_set = set()

    if type == 'artists':
        fieldnames = artist_fieldnames

    with open(csv_filename, newline='', encoding='UTF8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            id_set.add(row[fieldnames[0]])

    return id_set        

def read_universe_data_from_csv(type):
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

def generate_candidate_list(playlist):
    return playlist

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
    print(request_url)
    if response.status_code == 401:
        token_type, access_token = refresh_access_token()
        auth_payload = token_type + '  ' + access_token
        headers = {
            'Authorization': auth_payload,
        }
        response = requests.get(request_url, headers=headers)
    elif response.status_code == 429:
        retry_after_secs = int(response.headers['retry-after']) + 1
        print('Rate Limit Exceeded, sleeping for ' + str(retry_after_secs) + ' seconds')
        time.sleep(retry_after_secs)
        response = requests.get(request_url, headers=headers)

    return response, headers    

def fetch_artist_data():
    # Get access token and build auth headers
    token_type, access_token = refresh_access_token()
    # token_type, access_token = refresh_access_token()
    auth_payload = token_type + '  ' + access_token
    headers = {
        'Authorization': auth_payload,
    }

    # Load already fetched ids
    fetched_artists = load_ids_from_csv('artists')
    
    # Load all artist ids in the universe
    all_artist_ids = read_universe_data_from_csv('artists')

    for idx in range(len(all_artist_ids)):
        artist_id = all_artist_ids[idx]

        # Don't duplicate effort
        if artist_id in fetched_artists:
            continue

        # Rate limit throttling
        # time.sleep(1)
        
        # Populate artist data
        artist_data = {}
        
        response = requests.get('https://api.spotify.com/v1/artists/' + artist_id, headers=headers)
        
        while response.status_code != 200:
            request_url = 'https://api.spotify.com/v1/artists/' + artist_id
            response, headers = retry_http_call(response, request_url, headers)
        
        response_dict = json.loads(response.text)

        artist_data['artist_id'] = artist_id
        artist_data['artist_name'] = response_dict['name']
        artist_data['artist_genres'] = response_dict['genres']
        artist_data['artist_followers'] = response_dict['followers']['total']
        artist_data['artist_popularity'] = response_dict['popularity']
        artist_data['artist_type'] = response_dict['type']

        # Fetch artist top tracks            
        artist_data['artist_top_tracks'] = []

        response = requests.get('https://api.spotify.com/v1/artists/' + artist_id + '/top-tracks?market=ES', headers=headers)
        
        while response.status_code != 200:
            request_url = 'https://api.spotify.com/v1/artists/' + artist_id + '/top-tracks?market=ES'
            response, headers = retry_http_call(response, request_url, headers)
        
        response_dict = json.loads(response.text)
        for track in response_dict['tracks']:
            artist_data['artist_top_tracks'].append(track['id'])
        
        # Fetch related artists
        artist_data['related_artists'] = []
        
        response = requests.get('https://api.spotify.com/v1/artists/' + artist_id + '/related-artists', headers=headers)
        while response.status_code != 200:
            request_url = 'https://api.spotify.com/v1/artists/' + artist_id + '/related-artists'
            response, headers = retry_http_call(response, request_url, headers)
            
        response_dict = json.loads(response.text)

        for rel_artist in response_dict['artists']:
            artist_data['related_artists'].append(rel_artist['id'])

        # Append data to csv
        print('Writing data for artist ' + str(idx) + ': ' + artist_data['artist_name'])
        append_data_to_csv(artist_data, 'artists')

def fetch_track_data():
    token_type, access_token = refresh_access_token()
    auth_payload = token_type + '  ' + access_token

    track_data_dicts = []
    all_track_ids = read_universe_data_from_csv('tracks')

    print(access_token)
    count = 0

    for track_id in all_track_ids:
        if count > 0:
            break

        track_data = { 'track_id' : track_id }

        headers = {
            'Authorization': auth_payload,
        }

        response = requests.get('https://api.spotify.com/v1/tracks/' + track_id, headers=headers)

        if(response.status_code == 401):
            access_token = refresh_access_token()
        else:
            response_dict = json.loads(response.text)
            track_data['artist_name'] = response_dict['name']
        track_data_dicts.append(track_data)

        count += 1

    write_data_to_csv(track_data_dicts, 'track')