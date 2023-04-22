import json
import os

def read_all_files(data_address):
    print(f'Reading JSON files from directory {data_address}')

    playlist_data = []
    files = os.listdir(data_address)

    for i in range(3):
        with open(data_address + files[i]) as f:
            json_data = json.load(f)
            playlist_data.append(json_data['playlists'])

    return playlist_data

if __name__ == '__main__':
    print('Running Model...')

    data_adress = input("Enter the path of the data directory (leave blank if unsure): ")
    if data_adress:
        playlist_data = read_all_files(data_adress)
    else:
        playlist_data = read_all_files('../spotify_million_playlist_dataset/data/')

    # print(playlist_data[0][0]['tracks'][0])

    print('Finished Running Model.')