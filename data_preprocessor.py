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
            except Exception as e:
                print(f'Failed to read file {filename} because of error: {str(e)}')    
            finally:
                f.close()        

    write_universe_data_to_csv(all_artists, type='artists') # len = 295860
    write_universe_data_to_csv(all_tracks, type='tracks')   # len = 2262292
    write_universe_data_to_csv(all_albums, type='albums')   # len = 734684     
