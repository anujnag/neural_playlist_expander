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
    
    with open(csv_filename, 'w', newline='', encoding='UTF8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        print(data_dicts)
        for dict in data_dicts:
            writer.writerow(dict)

def read_data_from_csv(type):
    csv_filename = type + '_data.csv'

    if type == 'artist':
        fieldnames = artist_fieldnames

    with open(csv_filename, newline='', encoding='UTF8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            print(row[fieldnames[1]])

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

def fetch_artist_data():
    token_type, access_token = refresh_access_token()
    auth_payload = token_type + '  ' + access_token

    artist_data_dicts = []
    all_artist_ids = read_universe_data_from_csv('artists')

    for i in range(0, 250, 50):
        artist_ids = ','.join(all_artist_ids[i:i+50])
        print(i)
        headers = {
            'Authorization': auth_payload,
        }

        # response = requests.get('https://api.spotify.com/v1/artists/' + artist_id, headers=headers)
        response_batch = requests.get('https://api.spotify.com/v1/artists?ids=' + artist_ids, headers=headers)

        while response_batch.status_code != 200:
            if response_batch.status_code == 401:
                token_type, access_token = refresh_access_token()
                auth_payload = token_type + '  ' + access_token
                headers = {
                    'Authorization': auth_payload,
                }
                response_batch = requests.get('https://api.spotify.com/v1/artists?ids=' + artist_ids, headers=headers)
            elif response_batch.status_code == 429:
                print('Rate Limit Exceeded, sleeping for 4 seconds')
                time.sleep(4)
                response_batch = requests.get('https://api.spotify.com/v1/artists?ids=' + artist_ids, headers=headers)
        
        response_batch_dict = json.loads(response_batch.text)
        
        for artist in response_batch_dict['artists']:
            artist_data = {}
            artist_data['artist_id'] = artist['id']
            artist_data['artist_name'] = artist['name']
            artist_data['artist_genres'] = artist['genres']
            artist_data['artist_followers'] = artist['followers']['total']
            artist_data['artist_popularity'] = artist['popularity']
            artist_data['artist_type'] = artist['type']

            # fetch artist top tracks
            headers = {
                'Authorization': auth_payload,
            }
            response = requests.get('https://api.spotify.com/v1/artists/' + artist['id'] + '/top-tracks?market=ES', headers=headers)
            
            while response.status_code != 200:
                if response.status_code == 401:
                    token_type, access_token = refresh_access_token()
                    auth_payload = token_type + '  ' + access_token
                    headers = {
                        'Authorization': auth_payload,
                    }
                    response = requests.get('https://api.spotify.com/v1/artists/' + artist['id'] + '/top-tracks?market=ES', headers=headers)
                elif response.status_code == 429:
                    print('Rate Limit Exceeded, sleeping for 4 seconds')
                    time.sleep(4)
                    response = requests.get('https://api.spotify.com/v1/artists/' + artist['id'] + '/top-tracks?market=ES', headers=headers)
            
            artist_data['artist_top_tracks'] = []
            try:
                response_dict = json.loads(response.text)
                for track in response_dict['tracks']:
                    artist_data['artist_top_tracks'].append(track['id'])
            except Exception as e: # work on python 3.x
                print('Failed to get top tracks for artist id ' + artist['id'] + ', received response ' + response.text)
                print('Error Message: ' + str(e))     

            # fetch related artists
            headers = {
                'Authorization': auth_payload,
            }
            response = requests.get('https://api.spotify.com/v1/artists/' + artist['id'] + '/related-artists', headers=headers)

            while response.status_code != 200:
                if response.status_code == 401:
                    token_type, access_token = refresh_access_token()
                    auth_payload = token_type + '  ' + access_token
                    headers = {
                        'Authorization': auth_payload,
                    }
                    response = requests.get('https://api.spotify.com/v1/artists/' + artist['id'] + '/related-artists', headers=headers)
                elif response.status_code == 429:
                    print('Rate Limit Exceeded, sleeping for 4 seconds')
                    time.sleep(4)
                    response = requests.get('https://api.spotify.com/v1/artists/' + artist['id'] + '/related-artists', headers=headers)
            
            artist_data['related_artists'] = []
            try:
                response_dict = json.loads(response.text)
                for rel_artist in response_dict['artists']:
                    artist_data['related_artists'].append(rel_artist['id'])
            except Exception as e: # work on python 3.x
                print('Failed to get related artists for artist id ' + artist['id'] + ', received response ' + response.text)
                print('Error Message: ' + str(e))    
                
            artist_data_dicts.append(artist_data)

    write_data_to_csv(artist_data_dicts, 'artist')

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