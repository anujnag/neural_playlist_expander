import argparse
import csv
import random
import torch
import torch.nn as nn
import torch.optim as optim

import consts
import web_api
import utils

from model import LightTrackEncoder, DeepTrackEncoder
from metrics import evaluate_metrics

def get_train_val_split(train_ratio):
    all_ids = list(range(0, 1000000))
    random.shuffle(all_ids)

    split_idx = int(len(all_ids) * train_ratio)
    train_ids = all_ids[:split_idx]
    val_ids = all_ids[split_idx:]
    return train_ids, val_ids

def train_encoder(train_ids):
    # Load all track ids in the universe
    all_track_ids = utils.read_universe_from_csv('tracks')

    # Load already processed data
    processed_tracks = utils.get_processed_tracks()
    processed_artists = utils.get_processed_artists()
    processed_albums = utils.get_processed_albums()
    
    model = LightTrackEncoder()
    criterion = nn.TripletMarginLoss(margin=50)
    optimizer = optim.Adam(model.parameters(), lr=0.0001)

    for epoch in range(100):
        epoch_loss = 0      

        with open('playlists_data.csv', newline='', encoding='UTF8') as csvfile:
            reader = csv.DictReader(csvfile)
            next(reader, None) # skip header
            for row in reader:
                # Load IDs for training
                playlist_track_ids = row['playlist_tracks'].strip('][').replace("\'", "").split(", ")
                positive_track_id = utils.get_positive_track(playlist_track_ids)
                negative_track_id = utils.get_negative_track(playlist_track_ids, all_track_ids)

                # Ensure feature data for all track ids is cached locally
                processed_tracks = web_api.fetch_track_data(
                    playlist_track_ids + [negative_track_id],
                    processed_tracks
                )

                # Build feature tensors
                playlist_features, pos_track_features, neg_track_features = web_api.build_training_features(
                    playlist_track_ids, positive_track_id, negative_track_id
                )

                # Normalize input features
                playlist_features = nn.functional.normalize(playlist_features, dim=0)
                pos_track_features = nn.functional.normalize(pos_track_features, dim=0)
                neg_track_features = nn.functional.normalize(neg_track_features, dim=0)

                # Compute encodings
                playlist_embedding = model(playlist_features)
                pos_track_embedding = model(pos_track_features)
                neg_track_embedding = model(neg_track_features)

                loss = criterion(playlist_embedding, pos_track_embedding, neg_track_embedding)
                epoch_loss += loss.item()

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                print('Loss for ' + row['playlist_id'] + ' playlist: ' + str(loss.item()))

            print(f'Epoch {epoch} loss = {epoch_loss}')

            # evaluate model
            model.eval()

            with torch.no_grad():
                mean_rprecision, mean_ndcg, mean_rec_song_clicks, processed_tracks, processed_artists, processed_albums = evaluate_metrics(
                      model, processed_tracks, processed_artists, processed_albums
                )

                print(f'Evaluation Stats: Mean R-Precision: {mean_rprecision}, Mean NDCG: {mean_ndcg}, Mean Rec Song Clicks: {mean_rec_song_clicks}')
            
            model.train()

        csvfile.close()

def main(args):
    random.seed(10)

    train_ids, val_ids = get_train_val_split(0.999)

    if args.train:
        print('Training Encoder...')
        train_encoder(train_ids)
        print('Finished Training Model.')
    
    if args.eval:
        print('Evaluating Model')
        mean_rprecision, mean_ndcg, mean_rec_song_clicks = evaluate_metrics(val_ids)
        print(f"Mean R-Precision: {mean_rprecision}, Mean NDCG: {mean_ndcg}, Mean Rec Song Clicks: {mean_rec_song_clicks}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train/Evaluate Playlist Recommendation")
    parser.add_argument("--train", type=bool, default=False, help="Train encoder from scratch")
    parser.add_argument("--eval", type=bool, default=True, help="Evaluate performance on metrics")

    args = parser.parse_args()
    main(args)
