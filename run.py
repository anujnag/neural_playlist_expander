import torch
import torch.nn as nn
import torch.optim as optim

from data_preprocessor import read_all_files
from model import LightNet, DeepNet
from utils import get_positive_track, get_negative_track

num_features = 15

def train(training_data, all_tracks):
    net = DeepNet()

    criterion = nn.TripletMarginLoss(margin=0.5, p=2)
    optimizer = optim.Adam(net.parameters(), lr=0.0001)

    for epoch in range(100):
        epoch_loss = 0            
        for playlist in training_data:
            playlist_features = torch.zeros()
            for track in playlist:
                playlist_features += track / len(playlist)

            positive_track = get_positive_track(playlist)
            negative_track = get_negative_track(playlist, all_tracks)
            
            playlist_embedding = net(playlist_features)
            positive_embedding = net(positive_track)
            negative_embedding = net(negative_track)

            score_pos = torch.dot(playlist_embedding, positive_embedding)
            score_neg = torch.dot(playlist_embedding, negative_embedding)
            loss = criterion(torch.linalg.norm(playlist_embedding), score_pos, score_neg)
            epoch_loss += loss.item()

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        if epoch % 100 == 0:
            print(f'Epoch {epoch} loss = {epoch_loss}')

if __name__ == '__main__':
    print('Running Model...')

    data_adress = input("Enter the path of the data directory (leave blank if unsure): ")
    if data_adress:
        playlist_data = read_all_files(data_adress)
    else:
        playlist_data = read_all_files('../spotify_million_playlist_dataset/data/')

    # print(playlist_data)

    print('Finished Running Model.')