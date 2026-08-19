import torch
import torch.nn as nn
from torchvision import models

class Bottle_Detection_Model(nn.Module):
    def __init__(self):
        super().__init__()
        self.resnet = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        self.resnet.fc = nn.Linear(512, 5)

    def forward(self, inputs):
        out = self.resnet(inputs)
        box = torch.sigmoid(out[:, :4])
        confidence = out[:, 4]
        return torch.cat((box, confidence.unsqueeze(1)), dim=1)




if __name__ == '__main__':
    attempt = Bottle_Detection_Model()