import csv
import torch
import torch.nn as nn
import torch.optim as optim

from model import LightNet, DeepNet
from feature_builder import build_feature_tensors, fetch_track_data, read_universe_from_csv
from utils import get_positive_track, get_negative_track


def train():
    # Load all track ids in the universe
    all_track_ids = read_universe_from_csv('tracks')

    # net = DeepNet()

    # criterion = nn.TripletMarginLoss(margin=0.5, p=2)
    # optimizer = optim.Adam(net.parameters(), lr=0.0001)

    for epoch in range(1):
        epoch_loss = 0      

        with open('playlists_data.csv', newline='', encoding='UTF8') as csvfile:
            reader = csv.DictReader(csvfile)
            next(reader, None) # skip header
            for row in reader:
                playlist_track_ids = row['playlist_tracks'].strip('][').replace("\'", "").split(", ")
                positive_track_id = get_positive_track(playlist_track_ids)
                negative_track_id = get_negative_track(playlist_track_ids, all_track_ids)

                # Ensure feature data for all track ids is cached locally
                fetch_track_data(playlist_track_ids + [negative_track_id])

                # Build feature tensors
                playlist_embedding, pos_track_embedding, neg_track_embedding = build_feature_tensors(
                    playlist_track_ids, positive_track_id, negative_track_id
                )

        csvfile.close()
        

        #     playlist_embedding = net(playlist_features)
        #     positive_embedding = net(positive_track)
        #     negative_embedding = net(negative_track)

        #     score_pos = torch.dot(playlist_embedding, positive_embedding)
        #     score_neg = torch.dot(playlist_embedding, negative_embedding)
        #     loss = criterion(torch.linalg.norm(playlist_embedding), score_pos, score_neg)
        #     epoch_loss += loss.item()

        #     optimizer.zero_grad()
        #     loss.backward()
        #     optimizer.step()

        # if epoch % 100 == 0:
        #     print(f'Epoch {epoch} loss = {epoch_loss}')

# def evaluate(net, eval_data):
#     metrics = evaluate_model(net, eval_data)
#     return metrics 

def main():
    print('Running Model...')

    # data_address = input("Enter the path of the data directory (leave blank if unsure): ")
    # if data_address is None:
    #     data_address = '../spotify_million_playlist_dataset/data/'

    train()
    # all_tracks = read_universe_data_from_csv('tracks')
    # model = train(data_address, all_tracks)
    # evaluate(model, data_address)

    print('Finished Running Model.')

if __name__ == '__main__':
    main()