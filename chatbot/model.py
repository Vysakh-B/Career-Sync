import torch
import torch.nn as nn
import json
import os
from django.conf import settings

# Define the NeuralNet model (same as your training model)
class NeuralNet(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(NeuralNet, self).__init__()
        self.l1 = nn.Linear(input_size, hidden_size)
        self.l2 = nn.Linear(hidden_size, hidden_size)
        self.l3 = nn.Linear(hidden_size, num_classes)
        self.relu = nn.ReLU()

    def forward(self, x):
        out = self.l1(x)
        out = self.relu(out)
        out = self.l2(out)
        out = self.relu(out)
        out = self.l3(out)
        return out

# Load the trained model
def load_model():
    model_path = os.path.join(settings.BASE_DIR, "chatbot/data.pth")
    data = torch.load(model_path, map_location=torch.device('cpu'))

    input_size = data["input_size"]
    hidden_size = data["hidden_size"]
    output_size = data["output_size"]
    model_state = data["model_state"]

    model = NeuralNet(input_size, hidden_size, output_size)
    model.load_state_dict(model_state)
    model.eval()

    return model, data["all_words"], data["tags"]

# Load the model once when the server starts
chatbot_model, all_words, tags = load_model()
