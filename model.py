import torch.nn as nn
from consts import track_feature_dim

class LightTrackEncoder(nn.Module):
    def __init__(self):
        super(LightTrackEncoder, self).__init__()
        self.act = nn.ReLU()
        self.fc1 = nn.Linear(track_feature_dim, 10)
        self.fc2 = nn.Linear(10, 10)
        self.fc3 = nn.Linear(10, 10)        
        self.fc4 = nn.Linear(10, 32)

    def forward(self, x):
        x = self.act(self.fc1(x))
        x = self.act(self.fc2(x))
        x = self.act(self.fc3(x))
        return self.fc4(x)

class DeepTrackEncoder(nn.Module):
    def __init__(self):
        super(DeepTrackEncoder, self).__init__()
        self.act = nn.ReLU()
        self.fc1 = nn.Linear(track_feature_dim, 10)
        self.fc2 = nn.Linear(10, 10)
        self.fc3 = nn.Linear(10, 10)
        self.fc4 = nn.Linear(10, 10)
        self.fc5 = nn.Linear(10, 10)
        self.fc6 = nn.Linear(10, 10)
        self.fc7 = nn.Linear(10, 10)        
        self.fc8 = nn.Linear(10, 32)

    def forward(self, x):
        x = self.act(self.fc1(x))
        x = self.act(self.fc2(x))
        x = self.act(self.fc3(x))
        x = self.act(self.fc4(x))
        x = self.act(self.fc5(x))
        x = self.act(self.fc6(x))
        x = self.act(self.fc7(x))
        return self.fc8(x)        