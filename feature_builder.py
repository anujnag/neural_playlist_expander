import csv
import json
import requests

artist_fieldnames = ['artist_id', 'artist_name']
client_id = 'CLIENT-ID' # Masked out entry, update while using
client_secret = 'CLIENT-SECRET' # Masked out entry, update while using

def write_data_to_csv(data_dicts, type):
    csv_filename = type + '_data.csv'
    
    if type == 'artist':
        fieldnames = artist_fieldnames
    
    with open(csv_filename, 'w', newline='', encoding='UTF8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
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

def read_all_data_from_csv(type):
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
    return token_type, access_token

def fetch_artist_data():
    token_type, access_token = refresh_access_token()
    auth_payload = token_type + '  ' + access_token

    artist_data_dicts = []
    all_artist_ids = read_all_data_from_csv('artists')

    print(access_token)
    count = 0

    for artist_id in all_artist_ids:
        if count > 100:
            break

        artist_data = { 'artist_id' : artist_id }

        headers = {
            'Authorization': auth_payload,
        }

        response = requests.get('https://api.spotify.com/v1/artists/' + artist_id, headers=headers)

        if(response.status_code == 401):
            access_token = refresh_access_token()
        else:
            response_dict = json.loads(response.text)
            artist_data['artist_name'] = response_dict['name']
        artist_data_dicts.append(artist_data)

        count += 1

    write_data_to_csv(artist_data_dicts, 'artist')