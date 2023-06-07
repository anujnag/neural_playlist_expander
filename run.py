import csv
import torch
import torch.nn as nn
import torch.optim as optim

import feature_builder
import utils

from model import LightNet, DeepNet

def train():
    # Load all track ids in the universe
    all_track_ids = utils.read_universe_from_csv('tracks')

    # Load already fetched ids
    prefetched_tracks = utils.load_ids_from_csv('tracks')

    net = LightNet()

    # criterion = nn.TripletMarginLoss(margin=0.5, p=2)
    # optimizer = optim.Adam(net.parameters(), lr=0.0001)

    for epoch in range(1):
        epoch_loss = 0      

        with open('playlists_data.csv', newline='', encoding='UTF8') as csvfile:
            reader = csv.DictReader(csvfile)
            next(reader, None) # skip header
            for row in reader:
                playlist_track_ids = row['playlist_tracks'].strip('][').replace("\'", "").split(", ")
                positive_track_id = utils.get_positive_track(playlist_track_ids)
                negative_track_id = utils.get_negative_track(playlist_track_ids, all_track_ids)

                # Ensure feature data for all track ids is cached locally
                feature_builder.fetch_track_data(playlist_track_ids + [negative_track_id], prefetched_tracks)

                prefetched_tracks.update(playlist_track_ids + [negative_track_id])

                # Build feature tensors
                playlist_features, pos_track_features, neg_track_features = feature_builder.build_training_features(
                    playlist_track_ids, positive_track_id, negative_track_id
                )

                playlist_embedding = net(playlist_features)
                pos_track_embedding = net(pos_track_features)
                neg_track_embedding = net(neg_track_features)

                # score_pos = torch.dot(playlist_embedding, positive_embedding)
                # score_neg = torch.dot(playlist_embedding, negative_embedding)
                # loss = criterion(torch.linalg.norm(playlist_embedding), score_pos, score_neg)
                # epoch_loss += loss.item()

                # optimizer.zero_grad()
                # loss.backward()
                # optimizer.step()

            if epoch % 100 == 0:
                print(f'Epoch {epoch} loss = {epoch_loss}')

        csvfile.close()

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