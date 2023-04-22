import json
import os

def read_all_files(data_address):
    print(f'Reading JSON files from directory {data_address}')

    training_data = []
    files = os.listdir(data_address)
    user_id = 0

    for i in range(3):
        with open(data_address + files[i]) as f:
            # parse playlist data
            json_data = json.load(f)
            for playlist in json_data['playlists']:
                playlist_data = {}
                playlist_data['user_id'] = user_id
                playlist_data['playlist_name'] = playlist['name']
                playlist_data['tracks'] = playlist['tracks']
                                    
                training_data.append(playlist_data)
            
            user_id += 1


    return training_data

if __name__ == '__main__':
    print('Running Model...')

    data_adress = input("Enter the path of the data directory (leave blank if unsure): ")
    if data_adress:
        playlist_data = read_all_files(data_adress)
    else:
        playlist_data = read_all_files('../spotify_million_playlist_dataset/data/')

    print(playlist_data)

    print('Finished Running Model.')