import random
from consts import blacklisted_track_ids
from feature_builder import generate_candidate_list

def get_positive_track(playlist_track_ids):
    idx = random.randint(0, len(playlist_track_ids))
    track = playlist_track_ids[idx]
    return track

def get_negative_track(playlist_track_ids, all_track_ids):
    idx = random.randint(0, len(all_track_ids) - 1)    
    track = all_track_ids[idx]
    while track in playlist_track_ids and track not in blacklisted_track_ids:
        idx = random.randint(0, len(all_track_ids) - 1)    
        track = all_track_ids[idx]

    return track

def generate_candidate_list(playlist):
    # code added in a private file to hide API keys and access tokens
    return generate_candidate_list(playlist)       