import random
from web_api import generate_candidate_list

def get_positive_track(playlist):
    idx = random.randint(0, len(playlist))
    track = playlist[idx]
    return track

def get_negative_track(playlist, all_tracks):
    idx = random.randint(0, len(all_tracks))    
    track = all_tracks[idx]
    while track in playlist:
        idx = random.randint(0, len(all_tracks))    
        track = all_tracks[idx]

    return track

def generate_candidate_list(playlist):
    # code added in a private file to hide API keys and access tokens
    return generate_candidate_list(playlist)       