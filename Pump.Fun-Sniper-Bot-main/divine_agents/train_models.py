import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

class PricePredictor(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(input_size=10, hidden_size=64, num_layers=2, batch_first=True)
        self.fc = nn.Linear(64, 1)
        
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        return self.fc(lstm_out[:, -1, :])

class PatternRecognizer(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv1d(1, 32, kernel_size=3)
        self.conv2 = nn.Conv1d(32, 64, kernel_size=3)
        self.fc = nn.Linear(64, 5)  # 5 pattern types
        
    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = torch.relu(self.conv2(x))
        x = torch.max_pool1d(x, kernel_size=x.size(-1))
        return self.fc(x.squeeze(-1))

def train_and_save_models():
    # Create dummy training data
    X_price = torch.randn(100, 20, 10)  # 100 samples, 20 timesteps, 10 features
    y_price = torch.randn(100, 1)
    
    X_pattern = torch.randn(100, 1, 30)  # 100 samples, 1 channel, 30 timesteps
    y_pattern = torch.randint(0, 5, (100,))
    
    # Train price predictor
    price_model = PricePredictor()
    optimizer = optim.Adam(price_model.parameters())
    criterion = nn.MSELoss()
    
    for _ in range(100):
        optimizer.zero_grad()
        output = price_model(X_price)
        loss = criterion(output, y_price)
        loss.backward()
        optimizer.step()
    
    # Train pattern recognizer
    pattern_model = PatternRecognizer()
    optimizer = optim.Adam(pattern_model.parameters())
    criterion = nn.CrossEntropyLoss()
    
    for _ in range(100):
        optimizer.zero_grad()
        output = pattern_model(X_pattern)
        loss = criterion(output, y_pattern)
        loss.backward()
        optimizer.step()
    
    # Save models
    price_model = torch.jit.script(price_model)
    pattern_model = torch.jit.script(pattern_model)
    
    price_model.save("models/price_predictor.pt")
    pattern_model.save("models/pattern_recognizer.pt")
    
    print("Models trained and saved!")

if __name__ == "__main__":
    train_and_save_models()
