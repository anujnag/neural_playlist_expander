import csv
import json
import os
import random
import time
import torch
import spotipy

import utils

from itertools import islice
from spotipy.oauth2 import SpotifyClientCredentials

from consts import SpotifyApiEndpoint, track_feature_dim, track_feature_map

def build_track_feature_tensor(track_features):
    track_tensor = torch.zeros(track_feature_dim)
    
    for idx in range(track_feature_dim):
        track_tensor[idx] = float(track_features[track_feature_map[idx]])

    return track_tensor

def build_playlist_feature_tensor(playlist_track_features):
    playlist_tensor = torch.zeros(track_feature_dim)
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

def fetch_track_data(track_ids, feature_type: SpotifyApiEndpoint):
    def chunks(iterable, size):
        iterator = iter(iterable)
        for first in iterator:
            yield [first] + list(islice(iterator, size - 1))

    csv_file_path = "all_tracks.csv"  # Path to the CSV file containing IDs
    base_path = "./features/tracks/audio_features/"  # Base path where JSON files will be saved

    # Read IDs from the CSV file
    input_ids = utils.read_ids_from_csv(csv_file_path)

    # Filter out IDs that already have a response file
    filtered_ids = [
        id for id in input_ids 
        if not os.path.exists(os.path.join(base_path, f"{id}.json")) or
        os.path.getsize(os.path.join(base_path, f"{id}.json")) == 0
    ]

    random.shuffle(filtered_ids)

    auth_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(auth_manager=auth_manager)

    # Fetch and save JSON for each chunk of 100 IDs
    for ids_chunk in chunks(filtered_ids, 100):
        time.sleep(10)
        try:
            # Join the chunk of IDs into a comma-separated string
            ids_list = [f"spotify:track:{id}" for id in ids_chunk]
            
            # Make the request
            features = sp.audio_features(tracks=ids_list)
            
            # Save each ID's JSON data to its corresponding file
            # Save each track's JSON data to its corresponding file
            for track_data in features:
                track_id = track_data['id']
                file_path = os.path.join(base_path, f"{track_id}.json")
                if track_data:  # Check if the track data is not empty
                    with open(file_path, 'w') as json_file:
                        json.dump(track_data, json_file, indent=4)
                    print(f"JSON data for track ID {track_id} successfully saved to {file_path}")
                else:
                    print(f"Track ID {track_id} has an empty response. Skipping.")
        
        except Exception as e:
            print(f"An error occurred for IDs {ids_chunk}: {e}")