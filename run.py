import torch
import torch.nn as nn
import torch.optim as optim

from data_preprocessor import read_all_files
from model import Net

def train():
    net = Net()

    input_num = [1, 2, 3, 5, 6, 7, 9, 10, 11, 12, 14, 19, 200, 14]
    criterion = nn.MSELoss()
    optimizer = optim.Adam(net.parameters(), lr=0.0002)

    for epoch in range(3000):
        epoch_loss = 0
        for num in range(20):
            tensor_num = torch.zeros(1, 1)
            target_tensor = torch.zeros(1, 1)
            target_tensor[0][0] = num**2
            tensor_num[0][0] = num
            output = net(tensor_num)
            loss = criterion(output, target_tensor)
            epoch_loss += loss.item()

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        if epoch % 100 == 0:
            print(f'Epoch {epoch} loss = {epoch_loss / len(input_num)}')

    net.eval()
    with torch.no_grad():
        tensor_num = torch.zeros(1, 1)
        tensor_num[0][0] = 10
        output = net(tensor_num)
        print(output)

if __name__ == '__main__':
    print('Running Model...')

    data_adress = input("Enter the path of the data directory (leave blank if unsure): ")
    if data_adress:
        playlist_data = read_all_files(data_adress)
    else:
        playlist_data = read_all_files('../spotify_million_playlist_dataset/data/')

    # print(playlist_data)

    print('Finished Running Model.')