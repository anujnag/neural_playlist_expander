import csv
import json
import os

def write_to_csv(playlist_data):
    with open('playlist_data.csv', 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=' ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(['Spam'] * 5 + ['Baked Beans'])
        spamwriter.writerow(['Spam', 'Lovely Spam', 'Wonderful Spam'])    
    return

def preprocess_artist_data():
    return

def read_from_csv():
    with open('playlist_data.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in spamreader:
            print(', '.join(row))
    return        

def read_all_files(data_address):
    print(f'Reading JSON files from directory {data_address}')

    training_data = []
    files = os.listdir(data_address)
    user_id = 0

    for i in range(1):
        with open(data_address + files[i]) as f:
            # parse playlist data
            json_data = json.load(f)
            for playlist in json_data['playlists']:
                playlist_data = {}
                playlist_data['user_id'] = user_id
                playlist_data['playlist_name'] = playlist['name']
                # for tracks in playlist_data:
                #     playlist_data['tracks'] = playlist['tracks']
                                    
                training_data.append(playlist_data)
            
            user_id += 1

    print(f'User ID: {user_id}')
    write_to_csv(training_data)

    return training_data

def split_dataset(playlist_data):
    return playlist_data    