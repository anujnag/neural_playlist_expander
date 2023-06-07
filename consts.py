#
# Maintaining all constants here
#

artist_feature_dim = 10
track_feature_dim = 6

playlist_fieldnames = ['playlist_id',
                       'playlist_tracks']

artist_fieldnames = ['artist_id', 
                    'artist_name',
                    'artist_genres',
                    'artist_followers',
                    'artist_popularity',
                    'artist_type',
                    'artist_top_tracks',
                    'related_artists']

track_fieldnames = ['track_id', 
                    'track_name',
                    'track_album', 
                    'track_artists',
                    'track_release_year',
                    'track_popularity', 
                    'track_duration', 
                    'track_disc_number',
                    'track_number',
                    'track_is_explicit',
                    'track_acousticness',
                    'track_danceability',
                    'track_energy', 
                    'track_instrumentalness', 
                    'track_key', 
                    'track_liveness', 
                    'track_loudness', 
                    'track_mode', 
                    'track_speechiness', 
                    'track_tempo', 
                    'track_time_signature', 
                    'track_valence',
                    'track_num_samples', 
                    'track_analysis_sample_rate', 
                    'track_analysis_channels', 
                    'track_end_of_fade_in', 
                    'track_start_of_fade_out', 
                    'track_tempo_confidence', 
                    'track_time_signature_confidence',
                    'track_key_confidence', 
                    'track_mode_confidence', 
                    'track_bars_start', 
                    'track_bars_duration', 
                    'track_bars_confidence', 
                    'track_beats_start', 
                    'track_beats_duration', 
                    'track_beats_confidence', 
                    'track_sections_start', 
                    'track_sections_duration', 
                    'track_sections_confidence',
                    'track_sections_loudness', 
                    'track_sections_tempo', 
                    'track_sections_tempo_confidence', 
                    'track_sections_key', 
                    'track_sections_key_confidence', 
                    'track_sections_mode', 
                    'track_sections_mode_confidence', 
                    'track_sections_time_signature', 
                    'track_sections_time_signature_confidence',
                    'track_segments_start', 
                    'track_segments_duration', 
                    'track_segments_confidence', 
                    'track_segments_loudness_start', 
                    'track_segments_loudness_max', 
                    'track_segments_loudness_max_time', 
                    'track_segments_loudness_end', 
                    'track_segments_pitches', 
                    'track_segments_timbre', 
                    'track_tatums_start', 
                    'track_tatums_duration', 
                    'track_tatums_confidence' ]


blacklisted_track_ids = ['42Vx9J2kK6qutsHyec9xgK', 
                         '6hhz7iJS9m8tfHDQ4MYbTj',
                         '4WHjf37BBXUo3WYBmJPdoU',
                         '6uQKuonTU8VKBz5SHZuQXD',
                         '62zfuyWkzuTZ2FE1MKroz7']

track_feature_map = {
    0: 'track_popularity',
    1: 'track_release_year',
    2: 'track_duration',
    3: 'track_acousticness',
    4: 'track_danceability',
    5: 'track_energy'
}                        
