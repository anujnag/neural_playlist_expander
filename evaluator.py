import csv
import math
import numpy as np
import random
import torch

import feature_builder

def generate_candidate_list(eval_playlist_ids, processed_tracks, processed_artists, processed_albums):
    candidate_lists = []
    visible_lists = []
    masked_lists = []

    with open('playlists_data.csv', newline='', encoding='UTF8') as csvfile:
        reader = csv.DictReader(csvfile)
        next(reader, None) # skip header
        for row in reader:
            if row['playlist_id'] not in eval_playlist_ids:
                continue

            suggested_tracks = []
            
            playlist_track_ids = row['playlist_tracks'].strip('][').replace("\'", "").split(", ")

            # mask one-third of playlist
            num_masked_tracks = len(playlist_track_ids) / 3
            masked_lists.append(playlist_track_ids[-num_masked_tracks:])
            visible_tracks = playlist_track_ids[:num_masked_tracks]

            processed_tracks = feature_builder.fetch_track_data(visible_tracks, processed_tracks)

            # (1) Find  artists in the playlist
            # (2) Find the artists related to the most appearing artists
            # (3) Find most appearing albums in the playlist
            visible_artists = []
            visible_albums = []
            related_artists = []
            for track in visible_tracks:
                # there can be multiple artists for same track
                for artist in processed_tracks[track]['artist']:
                    visible_artists.append(artist)
                
                visible_albums.append(processed_tracks[track]['album'])
                processed_artists = feature_builder.fetch_artist_data(visible_artists)
                for artist in visible_artists:
                    related_artists += processed_artists[artist]['related_artists']

            # suggest top tracks by all artists in the playlist
            for artist in visible_artists:
                suggested_tracks += processed_artists[artist]['artist_top_tracks']

            # suggest tracks in all the albums in the playlist
            for album in visible_albums:
                suggested_tracks += processed_albums[album]['tracks']

            # suggest top tracks by artists related to artists in the playlist
            for artist in related_artists:
                suggested_tracks += processed_artists[artist]['artist_top_tracks']

            candidate_lists.append(suggested_tracks)
            visible_lists.append(visible_tracks)    

    return candidate_lists, visible_lists, masked_lists

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

def calculate_rprecision(ranked_suggestions, masked_lists, num_eval_playlists):
    mean_rprecision = 0.0
    
    for suggestions, masked_tracks in zip(ranked_suggestions, masked_lists):
        count = 0
        for suggestion in suggestions[:len(masked_tracks)]:
            if suggestion in masked_tracks:
                count += 1

        rprecision = count / len(masked_tracks)
        mean_rprecision += rprecision / num_eval_playlists
    
    return mean_rprecision    

def calculate_ndcg(ranked_suggestions, masked_lists, num_eval_playlists):
    mean_ndcg = 0.0

    for suggestions, masked_tracks in zip(ranked_suggestions, masked_lists):
        count = 0
        for suggestion in suggestions:
            if suggestion in masked_tracks:
                count += 1

        idcg = 1.0
        for i in range(2, count+1):
            idcg += 1 / math.log(i, 2)        
    
        dcg = 0.0
        if suggestions[0] in masked_tracks:
            dcg += 1.0 

        for i in range(2, len(suggestions) + 1):
            if suggestions[i - 1] in masked_tracks:
                dcg += 1.0 / math.log(i, 2)

        ndcg = dcg / idcg
        mean_ndcg += ndcg / num_eval_playlists

    return mean_ndcg

def calculate_rec_song_clicks(ranked_suggestions, masked_lists, num_eval_playlists):
    mean_rec_song_clicks = 0.0
    
    for suggestions, masked_tracks in zip(ranked_suggestions, masked_lists):
        rec_song_clicks = 51

        for i in range(len(suggestions)):
            if suggestions[i] in masked_tracks:
                rec_song_clicks = math.floor(i / 10)
                break

        mean_rec_song_clicks += rec_song_clicks / num_eval_playlists

    return mean_rec_song_clicks

def evaluate_metrics(model, processed_tracks, processed_artists, processed_albums):
    num_eval_playlists = 5

    eval_playlist_ids = random.sample(range(0, 999999), num_eval_playlists)
    candidate_lists, visible_lists, masked_lists = generate_candidate_list(
        eval_playlist_ids, processed_tracks, processed_artists, processed_albums
    )
    
    ranked_suggestions = get_ranked_suggestions(model, visible_lists, candidate_lists)

    # calculate metrics
    mean_rprecision = calculate_rprecision(ranked_suggestions, masked_lists, num_eval_playlists)
    mean_ndcg = calculate_ndcg(ranked_suggestions, masked_lists, num_eval_playlists)
    mean_rec_song_clicks = calculate_rec_song_clicks(ranked_suggestions, masked_lists, num_eval_playlists)
    
    return mean_rprecision, mean_ndcg, mean_rec_song_clicks, processed_tracks, processed_artists, processed_albums
