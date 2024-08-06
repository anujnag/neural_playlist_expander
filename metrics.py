import csv
import math
import random
import torch
from tqdm import tqdm

import feature_builder

from utils import get_tracks_from_playlist_id

def generate_candidate_list(eval_playlist_ids, processed_tracks, processed_artists, processed_albums):
    candidate_lists = []
    visible_lists = []
    masked_lists = []

    with open('playlists_data.csv', newline='', encoding='UTF8') as csvfile:
        reader = csv.DictReader(csvfile)
        next(reader, None) # skip header
        for row in reader:
            if int(row['playlist_id']) not in eval_playlist_ids:
                continue

            suggested_tracks = []
            
            playlist_track_ids = row['playlist_tracks'].strip('][').replace("\'", "").split(", ")

            # mask one-third of playlist
            num_masked_tracks = math.ceil(len(playlist_track_ids) / 3)
            masked_lists.append(playlist_track_ids[-num_masked_tracks:])
            visible_tracks = playlist_track_ids[:-num_masked_tracks]

            processed_tracks = feature_builder.fetch_track_data(visible_tracks, processed_tracks)

            # (1) Find  artists in the playlist
            # (2) Find the artists related to the most appearing artists
            # (3) Find most appearing albums in the playlist
            visible_artists = []
            visible_albums = []
            related_artists = []
            for track in visible_tracks:
                track_artists = processed_tracks[track]['artist']
                # there can be multiple artists for same track
                for artist in track_artists:
                    visible_artists.append(artist)
                
                visible_albums.append(processed_tracks[track]['album'])
            
            visible_artists = list(set(visible_artists))
            processed_artists = feature_builder.fetch_artist_data(visible_artists, processed_artists)
            
            for artist in visible_artists:
                related_artists += processed_artists[artist]['related_artists']

            visible_albums = list(set(visible_albums))
            related_artists = list(set(related_artists))

            processed_albums = feature_builder.fetch_album_data(visible_albums, processed_albums)
            processed_artists = feature_builder.fetch_artist_data(related_artists, processed_artists)

            # suggest top tracks by all artists in the playlist
            for artist in visible_artists:
                suggested_tracks += processed_artists[artist]['top_tracks']

            # suggest tracks in all the albums in the playlist
            for album in visible_albums:
                suggested_tracks += processed_albums[album]['tracks']

            # suggest top tracks by artists related to artists in the playlist
            for artist in related_artists:
                suggested_tracks += processed_artists[artist]['top_tracks']

            suggested_tracks = list(set(suggested_tracks))
            processed_tracks = feature_builder.fetch_track_data(suggested_tracks, processed_tracks)

            candidate_lists.append(suggested_tracks)
            visible_lists.append(visible_tracks)    

    return candidate_lists, visible_lists, masked_lists, processed_tracks, processed_artists, processed_albums

def get_ranked_suggestions(model, visible_lists, candidate_lists):
    ranked_suggestions = []

    for visible_playlist, candidate_tracks in zip(visible_lists, candidate_lists):
        suggestion_scores = []
        visible_playlist_features, _, _ = feature_builder.build_training_features(visible_playlist, None, None)
        playlist_embedding = model(visible_playlist_features)
        for track in candidate_tracks:
            _, track_features, _ = feature_builder.build_training_features([], track, None)
            track_embedding = model(track_features)
            suggestion_scores.append(-torch.linalg_norm(playlist_embedding - track_embedding))

        ranked_suggestions.append(sorted(suggestion_scores))

    return ranked_suggestions    

def calculate_rprecision(ranked_suggestions, masked_playlist):
    intersection = 0

    # Note: ground truth mask contains duplicates - can't use set intersection
    for index, suggestion in enumerate(ranked_suggestions):
        if index >= len(masked_playlist):
            break
        if suggestion in masked_playlist:
            intersection += 1

    rprecision = intersection / len(masked_playlist)
    return rprecision

def calculate_ndcg(ranked_suggestions, masked_playlist):
    dcg = 0.0
    for index, suggestion in enumerate(ranked_suggestions):
        if suggestion in masked_playlist:
            dcg += 1.0 / math.log(index + 2, 2)

    idcg = 0.0
    for index in range(len(masked_playlist)):
        idcg += 1.0 / math.log(index + 2, 2)

    ndcg = dcg / idcg
    return ndcg

def calculate_rec_song_clicks(ranked_suggestions, masked_playlist):
    rec_song_clicks = 51

    for index, suggestion in enumerate(ranked_suggestions):
        if suggestion in masked_playlist:
            rec_song_clicks = math.floor(index / 10)
            break
    
    return rec_song_clicks

def evaluate_metrics(val_playlist_ids):
    all_rprecision = []
    all_ndcg = []
    all_rec_song_clicks = []
    
    for playlist_id in tqdm(val_playlist_ids):
        track_ids = get_tracks_from_playlist_id(playlist_id)
        num_unmasked = random.randint(0, len(track_ids) - 1)
        unmasked_playlist, masked_playlist = track_ids[:num_unmasked], track_ids[num_unmasked:]
        
        # Placeholder for generating ranked candidate list
        # candidate_lists, visible_lists, masked_lists, processed_tracks, processed_artists, processed_albums = generate_candidate_list(
        #     eval_playlist_ids, processed_tracks, processed_artists, processed_albums
        # )
    
        # ranked_suggestions = get_ranked_suggestions(model, visible_lists, candidate_lists)
        ranked_suggestions = masked_playlist

        # calculate metrics
        rprecision = calculate_rprecision(ranked_suggestions, masked_playlist)
        ndcg = calculate_ndcg(ranked_suggestions, masked_playlist)
        rec_song_clicks = calculate_rec_song_clicks(ranked_suggestions, masked_playlist)

        all_rprecision.append(rprecision)
        all_ndcg.append(ndcg)
        all_rec_song_clicks.append(rec_song_clicks)

    mean_rprecision = sum(all_rprecision) / len(all_rprecision)
    mean_ndcg = sum(all_ndcg) / len(all_ndcg)
    mean_rec_song_clicks = sum(all_rec_song_clicks) / len(all_rec_song_clicks)

    return mean_rprecision, mean_ndcg, mean_rec_song_clicks
