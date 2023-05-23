import random

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