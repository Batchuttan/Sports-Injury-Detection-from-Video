"""
Spatial-Temporal CNN + BiLSTM with Temporal Attention for Sports Action Recognition
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class TemporalAttention(nn.Module):
    def __init__(self, hidden_dim):
        super(TemporalAttention, self).__init__()
        self.attn = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.Tanh(),
            nn.Linear(hidden_dim // 2, 1, bias=False)
        )

    def forward(self, rnn_out):
        # rnn_out: (B, T, hidden_dim)
        scores = self.attn(rnn_out)  # (B, T, 1)
        weights = F.softmax(scores, dim=1)  # (B, T, 1)
        context = torch.sum(weights * rnn_out, dim=1)  # (B, hidden_dim)
        return context, weights

class SportsActionSTNet(nn.Module):
    """
    Spatial-Temporal Neural Network for 7-class sports activity recognition.
    Combines 1D Spatial-Temporal Convolutions + Bidirectional LSTM + Temporal Attention.
    """
    def __init__(self, in_features=95, num_classes=7, conv_dim=128, lstm_hidden=128, num_lstm_layers=2, dropout=0.4):
        super(SportsActionSTNet, self).__init__()
        
        # 1. Input Projection & Spatial-Temporal Convolutions
        self.conv1 = nn.Conv1d(in_features, conv_dim, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm1d(conv_dim)
        self.conv2 = nn.Conv1d(conv_dim, conv_dim, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm1d(conv_dim)
        self.conv_dropout = nn.Dropout(0.25)
        
        # Residual connection
        self.res_proj = nn.Conv1d(in_features, conv_dim, kernel_size=1) if in_features != conv_dim else nn.Identity()

        # 2. Bidirectional LSTM
        self.lstm = nn.LSTM(
            input_size=conv_dim,
            hidden_size=lstm_hidden,
            num_layers=num_lstm_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_lstm_layers > 1 else 0.0
        )
        
        # 3. Temporal Attention Pooling
        self.attention = TemporalAttention(lstm_hidden * 2)
        
        # 4. Classification MLP Head
        self.classifier = nn.Sequential(
            nn.Linear(lstm_hidden * 2, 128),
            nn.LayerNorm(128),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(128, 64),
            nn.GELU(),
            nn.Dropout(dropout / 2),
            nn.Linear(64, num_classes)
        )

    def forward(self, x):
        # x: (B, T, in_features)
        x_trans = x.transpose(1, 2)  # (B, in_features, T)
        
        res = self.res_proj(x_trans)
        h = F.gelu(self.bn1(self.conv1(x_trans)))
        h = self.conv_dropout(h)
        h = F.gelu(self.bn2(self.conv2(h)))
        h = h + res  # Residual addition
        
        h = h.transpose(1, 2)  # (B, T, conv_dim)
        
        lstm_out, _ = self.lstm(h)  # (B, T, lstm_hidden * 2)
        
        context, attn_weights = self.attention(lstm_out)  # (B, lstm_hidden * 2)
        
        logits = self.classifier(context)  # (B, num_classes)
        return logits, attn_weights

