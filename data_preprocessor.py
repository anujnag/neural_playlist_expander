import csv
import json
import os

def write_universe_data_to_csv(data, type):
    if type == 'artists':
        csvfile = 'all_artists.csv'
    elif type == 'albums':
        csvfile = 'all_albums.csv'
    elif type == 'tracks':
        csvfile = 'all_tracks.csv'

    with open(csvfile, 'w', encoding='UTF8') as f:
        # create the csv writer
        writer = csv.writer(f)
        writer.writerow(data)

def read_universe_data_from_json(data_address):
    print(f'Reading JSON files from directory {data_address}')

    files = os.listdir(data_address)

    all_artists = set()
    all_tracks = set()
    all_albums = set()
    for filename in files:
        with open(data_address + filename) as f:
            try:        
                json_data = json.load(f)
                for playlist in json_data['playlists']:
                    for track in playlist['tracks']:
                        artist_id = track['artist_uri'].split(":")[2]
                        album_id = track['album_uri'].split(":")[2]
                        track_id = track['track_uri'].split(":")[2]
                        all_artists.add(artist_id)
                        all_albums.add(album_id)
                        all_tracks.add(track_id)
            except Exception as e: # work on python 3.x
                print(f'Failed to read file {filename} because of error: {str(e)}')    
            finally:
                f.close()        

    write_universe_data_to_csv(all_artists, type='artists') # len = 295860
    write_universe_data_to_csv(all_tracks, type='tracks')   # len = 2262292
    write_universe_data_to_csv(all_albums, type='albums')   # len = 734684     

def read_all_files(data_address):
    print(f'Reading JSON files from directory {data_address}')

    training_data = []
    files = os.listdir(data_address)
    user_id = 0

    for filename in files:
        with open(data_address + filename) as f:
            try:        
                # parse playlist data
                json_data = json.load(f)
                # for playlist in json_data['playlists']:
                    # playlist_data = {}
                    # playlist_data['user_id'] = user_id
                    # playlist_data['playlist_name'] = playlist['name']
                    # for track in playlist['tracks']:
                        
                                        
                    # training_data.append(playlist_data)
                
                # user_id += 1
            except Exception as e: # work on python 3.x
                print(f'Failed to read file {filename} because of error: {str(e)}')    
            finally:
                f.close()

    return training_data

def split_dataset(playlist_data):
    return playlist_data