from concurrent.futures import process
import csv
import json
import requests
import time
import torch

import consts
import utils

def build_track_feature_tensor(track_features):
    track_tensor = torch.zeros(consts.track_feature_dim)
    
    for idx in range(consts.track_feature_dim):
        track_tensor[idx] = float(track_features[consts.track_feature_map[idx]])

    return track_tensor

def build_playlist_feature_tensor(playlist_track_features):
    playlist_tensor = torch.zeros(consts.track_feature_dim)
    num_tracks = len(playlist_track_features)

    for track_features in playlist_track_features:
        track_feature_tensor = build_track_feature_tensor(track_features)
        playlist_tensor += track_feature_tensor / num_tracks

    return playlist_tensor

def build_training_features(playlist_track_ids, positive_track_id, negative_track_id):
    track_count = 0
    track_limit = len(playlist_track_ids)

    if negative_track_id != None:
        track_limit += 1

    playlist_features = []
    pos_track_tensor = None
    neg_track_tensor = None
    
    with open('tracks_data.csv', newline='', encoding='UTF8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if track_count == track_limit:
                break

            # check if relevant entry            
            if row['track_id'] not in playlist_track_ids + [negative_track_id]:
                continue

            if row['track_id'] in playlist_track_ids:
                playlist_features.append(row)
                # check if this is also our positive track
                if positive_track_id != None and row['track_id'] == positive_track_id:
                    pos_track_tensor = build_track_feature_tensor(row)
                
            # check if this is our negative track
            if negative_track_id != None and row['track_id'] == negative_track_id:
                neg_track_tensor = build_track_feature_tensor(row)

            track_count += 1    

        csvfile.close()        

        playlist_tensor = build_playlist_feature_tensor(playlist_features)
    
    return playlist_tensor, pos_track_tensor, neg_track_tensor

def fetch_artist_data(artist_ids, processed_artists):
    # Get access token and build auth headers
    token_type, access_token = utils.refresh_access_token()
    auth_payload = token_type + '  ' + access_token
    headers = {
        'Authorization': auth_payload,
    }
    
    for artist_id in artist_ids:
        # Don't duplicate effort
        if artist_id in processed_artists.keys():
            continue

        # Rate limit throttling
        time.sleep(2)
        
        # Populate artist data
        artist_data = {}
        
        response = requests.get('https://api.spotify.com/v1/artists/' + artist_id, headers=headers)
        
        while response.status_code != 200:
            request_url = 'https://api.spotify.com/v1/artists/' + artist_id
            response, headers = utils.retry_http_call(response, request_url, headers)
        
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
            response, headers = utils.retry_http_call(response, request_url, headers)
        
        response_dict = json.loads(response.text)
        for track in response_dict['tracks']:
            artist_data['artist_top_tracks'].append(track['id'])
        
        # Fetch related artists
        artist_data['related_artists'] = []
        
        response = requests.get('https://api.spotify.com/v1/artists/' + artist_id + '/related-artists', headers=headers)
        while response.status_code != 200:
            request_url = 'https://api.spotify.com/v1/artists/' + artist_id + '/related-artists'
            response, headers = utils.retry_http_call(response, request_url, headers)
            
        response_dict = json.loads(response.text)

        for rel_artist in response_dict['artists']:
            artist_data['related_artists'].append(rel_artist['id'])

        # Append data to csv
        print('Writing data for artist: ' + artist_data['artist_name'])
        utils.append_data_to_csv(artist_data, 'artists')
        processed_artists[artist_id] = {
            'top_tracks': artist_data['artist_top_tracks'],
            'related_artists': artist_data['related_artists']
        }

    return processed_artists

def fetch_track_data(track_ids, processed_tracks):
    # Get access token and build auth headers
    token_type, access_token = utils.refresh_access_token()
    auth_payload = token_type + '  ' + access_token
    headers = {
        'Authorization': auth_payload,
    }
    
    for track_id in track_ids:        
        # Don't duplicate effort
        if track_id in processed_tracks.keys() or track_id in consts.blacklisted_track_ids:
            continue

        # Rate limit throttling
        time.sleep(2)
        
        # Populate track data
        track_data = {}
        
        response = requests.get('https://api.spotify.com/v1/tracks/' + track_id, headers=headers)
        
        while response.status_code != 200:
            request_url = 'https://api.spotify.com/v1/tracks/' + track_id
            response, headers = utils.retry_http_call(response, request_url, headers)
        
        response_dict = json.loads(response.text)

        track_data['track_id'] = track_id
        track_data['track_name'] = response_dict['name']
        track_data['track_number'] = response_dict['track_number']
        track_data['track_popularity'] = response_dict['popularity']
        track_data['track_is_explicit'] = response_dict['explicit']
        track_data['track_duration'] = response_dict['duration_ms']
        track_data['track_disc_number'] = response_dict['disc_number']
        track_data['track_album'] = response_dict['album']['id']
        track_data['track_release_year'] = response_dict['album']['release_date'].split('-')[0]
        track_data['track_artists'] = []
        for artist in response_dict['artists']:
            track_data['track_artists'].append(artist['id'])

        # Fetch track's audio features            
        response = requests.get('https://api.spotify.com/v1/audio-features/' + track_id, headers=headers)
        
        while response.status_code != 200:
            request_url = 'https://api.spotify.com/v1/audio-features/' + track_id
            response, headers = utils.retry_http_call(response, request_url, headers)
        
        response_dict = json.loads(response.text)
        track_data['track_acousticness'] = response_dict['acousticness']
        track_data['track_danceability'] = response_dict['danceability']
        track_data['track_energy'] = response_dict['energy']
        track_data['track_instrumentalness'] = response_dict['instrumentalness']
        track_data['track_key'] = response_dict['key']
        track_data['track_liveness'] = response_dict['liveness']
        track_data['track_loudness'] = response_dict['loudness']
        track_data['track_mode'] = response_dict['mode']
        track_data['track_speechiness'] = response_dict['speechiness']
        track_data['track_tempo'] = response_dict['tempo']
        track_data['track_time_signature'] = response_dict['time_signature']
        track_data['track_valence'] = response_dict['valence']

        # Fetch track's audio analysis
        response = requests.get('https://api.spotify.com/v1/audio-analysis/' + track_id, headers=headers)
        while response.status_code != 200:
            request_url = 'https://api.spotify.com/v1/audio-analysis/' + track_id
            response, headers = utils.retry_http_call(response, request_url, headers)
            
        response_dict = json.loads(response.text)
        track_data['track_num_samples'] = response_dict['track']['num_samples']
        track_data['track_analysis_sample_rate'] = response_dict['track']['analysis_sample_rate']
        track_data['track_analysis_channels'] = response_dict['track']['analysis_channels']        
        track_data['track_end_of_fade_in'] = response_dict['track']['end_of_fade_in']
        track_data['track_start_of_fade_out'] = response_dict['track']['start_of_fade_out']
        track_data['track_tempo_confidence'] = response_dict['track']['tempo_confidence']
        track_data['track_time_signature_confidence'] = response_dict['track']['time_signature_confidence']
        track_data['track_key_confidence'] = response_dict['track']['key_confidence']
        track_data['track_mode_confidence'] = response_dict['track']['mode_confidence']

        track_data['track_bars_start'] = []
        track_data['track_bars_duration'] = []
        track_data['track_bars_confidence'] = []
        for bar in response_dict['bars']:
            track_data['track_bars_start'].append(bar['start'])
            track_data['track_bars_duration'].append(bar['duration'])
            track_data['track_bars_confidence'].append(bar['confidence'])

        track_data['track_beats_start'] = []
        track_data['track_beats_duration'] = []
        track_data['track_beats_confidence'] = []
        for beat in response_dict['beats']:
            track_data['track_beats_start'].append(beat['start'])
            track_data['track_beats_duration'].append(beat['duration'])
            track_data['track_beats_confidence'].append(beat['confidence'])    

        track_data['track_sections_start'] = []
        track_data['track_sections_duration'] = []
        track_data['track_sections_confidence'] = []
        track_data['track_sections_loudness'] = []
        track_data['track_sections_tempo'] = []
        track_data['track_sections_tempo_confidence'] = []
        track_data['track_sections_key'] = []
        track_data['track_sections_key_confidence'] = []
        track_data['track_sections_mode'] = []
        track_data['track_sections_mode_confidence'] = []
        track_data['track_sections_time_signature'] = []
        track_data['track_sections_time_signature_confidence'] = []
        for section in response_dict['sections']:
            track_data['track_sections_start'].append(section['start'])
            track_data['track_sections_duration'].append(section['duration'])
            track_data['track_sections_confidence'].append(section['confidence'])
            track_data['track_sections_loudness'].append(section['loudness'])
            track_data['track_sections_tempo'].append(section['tempo'])
            track_data['track_sections_tempo_confidence'].append(section['tempo_confidence'])
            track_data['track_sections_key'].append(section['key'])
            track_data['track_sections_key_confidence'].append(section['key_confidence'])
            track_data['track_sections_mode'].append(section['mode'])
            track_data['track_sections_mode_confidence'].append(section['mode_confidence'])
            track_data['track_sections_time_signature'].append(section['time_signature'])
            track_data['track_sections_time_signature_confidence'].append(section['time_signature_confidence'])

        track_data['track_segments_start'] = []
        track_data['track_segments_duration'] = []
        track_data['track_segments_confidence'] = []
        track_data['track_segments_loudness_start'] = []
        track_data['track_segments_loudness_max'] = []
        track_data['track_segments_loudness_max_time'] = []
        track_data['track_segments_loudness_end'] = []
        track_data['track_segments_pitches'] = []
        track_data['track_segments_timbre'] = []
        for segment in response_dict['segments']:
            track_data['track_segments_start'].append(segment['start'])
            track_data['track_segments_duration'].append(segment['duration'])
            track_data['track_segments_confidence'].append(segment['confidence'])
            track_data['track_segments_loudness_start'].append(segment['loudness_start'])
            track_data['track_segments_loudness_max'].append(segment['loudness_max'])
            track_data['track_segments_loudness_max_time'].append(segment['loudness_max_time'])
            track_data['track_segments_loudness_end'].append(segment['loudness_end'])
            track_data['track_segments_pitches'].append(segment['pitches'])
            track_data['track_segments_timbre'].append(segment['timbre'])

        track_data['track_tatums_start'] = []
        track_data['track_tatums_duration'] = []
        track_data['track_tatums_confidence'] = []
        for tatum in response_dict['tatums']:
            track_data['track_tatums_start'].append(tatum['start'])
            track_data['track_tatums_duration'].append(tatum['duration'])
            track_data['track_tatums_confidence'].append(tatum['confidence'])

        # Append data to csv
        print('Writing data for track: ' + track_data['track_name'])
        utils.append_data_to_csv(track_data, 'tracks')
        processed_tracks[track_id] = {
            'artist': track_data['track_artists'],
            'album': track_data['track_album']
        }

    return processed_tracks

def fetch_album_data(album_ids, processed_albums):
    # Get access token and build auth headers
    token_type, access_token = utils.refresh_access_token()
    auth_payload = token_type + '  ' + access_token
    headers = {
        'Authorization': auth_payload,
    }
    
    for album_id in album_ids:        
        # Don't duplicate effort
        if album_id in processed_albums.keys():
            continue

        # Rate limit throttling
        time.sleep(2)
        
        # Populate album data
        album_data = {}
        
        response = requests.get('https://api.spotify.com/v1/albums/' + album_id, headers=headers)
        
        while response.status_code != 200:
            request_url = 'https://api.spotify.com/v1/albums/' + album_id
            response, headers = utils.retry_http_call(response, request_url, headers)
        
        response_dict = json.loads(response.text)

        album_data['album_id'] = album_id
        album_data['album_name'] = response_dict['name']
        album_data['album_type'] = response_dict['album_type']
        album_data['album_total_tracks'] = response_dict['total_tracks']
        album_data['album_available_markets'] = response_dict['available_markets']
        album_data['album_release_year'] = response_dict['release_date'].split('-')[0]
        album_data['album_genres'] = response_dict['genres']
        album_data['album_popularity'] = response_dict['popularity']
        
        album_data['album_artists'] = []
        for artist in response_dict['artists']:
            album_data['album_artists'].append(artist['id'])

        album_data['album_tracks'] = []
        for track in response_dict['tracks']['items']:
            album_data['album_tracks'].append(track['id'])

        # Append data to csv
        print('Writing data for album: ' + album_data['album_name'])
        utils.append_data_to_csv(album_data, 'albums')
        processed_albums[album_id] = {
            'tracks': album_data['album_tracks']
        }

    return processed_albums