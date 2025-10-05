"""
Model architectures for video-based unsafe action detection
"""
import torch
import torch.nn as nn
import torchvision.models as models
from torchvision.models import ResNet50_Weights, ResNet18_Weights


class VideoActionDetector(nn.Module):
    """
    3D CNN-based model for video action detection
    Uses 2D CNN backbone + temporal convolutions
    """
    
    def __init__(self, num_classes, backbone='resnet50', num_frames=16, 
                 dropout=0.5, pretrained=True):
        super(VideoActionDetector, self).__init__()
        
        self.num_classes = num_classes
        self.num_frames = num_frames
        
        # Load 2D CNN backbone
        if backbone == 'resnet50':
            weights = ResNet50_Weights.DEFAULT if pretrained else None
            base_model = models.resnet50(weights=weights)
            self.feature_dim = 2048
        elif backbone == 'resnet18':
            weights = ResNet18_Weights.DEFAULT if pretrained else None
            base_model = models.resnet18(weights=weights)
            self.feature_dim = 512
        else:
            raise ValueError(f"Unsupported backbone: {backbone}")
        
        # Remove the final FC layer
        self.backbone = nn.Sequential(*list(base_model.children())[:-2])
        
        # Spatial pooling
        self.spatial_pool = nn.AdaptiveAvgPool2d((1, 1))
        
        # Temporal modeling with 1D convolutions
        self.temporal_conv = nn.Sequential(
            nn.Conv1d(self.feature_dim, 512, kernel_size=3, padding=1),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            
            nn.Conv1d(512, 256, kernel_size=3, padding=1),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
        )
        
        # Temporal pooling
        self.temporal_pool = nn.AdaptiveAvgPool1d(1)
        
        # Classifier
        self.classifier = nn.Sequential(
            nn.Linear(256, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(128, num_classes)
        )
    
    def forward(self, x):
        """
        Args:
            x: Input tensor of shape (B, T, C, H, W)
                B = batch size
                T = number of frames
                C = channels (3)
                H, W = height, width
        
        Returns:
            logits: Output tensor of shape (B, num_classes)
        """
        batch_size, num_frames, C, H, W = x.shape
        
        # Reshape to process all frames through CNN: (B*T, C, H, W)
        x = x.view(batch_size * num_frames, C, H, W)
        
        # Extract spatial features
        features = self.backbone(x)  # (B*T, feature_dim, h, w)
        
        # Spatial pooling
        features = self.spatial_pool(features)  # (B*T, feature_dim, 1, 1)
        features = features.view(batch_size, num_frames, self.feature_dim)  # (B, T, feature_dim)
        
        # Reshape for temporal convolution: (B, feature_dim, T)
        features = features.permute(0, 2, 1)
        
        # Temporal modeling
        temporal_features = self.temporal_conv(features)  # (B, 256, T)
        
        # Temporal pooling
        pooled = self.temporal_pool(temporal_features)  # (B, 256, 1)
        pooled = pooled.squeeze(-1)  # (B, 256)
        
        # Classification
        logits = self.classifier(pooled)  # (B, num_classes)
        
        return logits


class LSTMActionDetector(nn.Module):
    """
    CNN + LSTM model for temporal action detection
    """
    
    def __init__(self, num_classes, backbone='resnet50', num_frames=16,
                 hidden_size=512, num_layers=2, dropout=0.5, pretrained=True):
        super(LSTMActionDetector, self).__init__()
        
        self.num_classes = num_classes
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # Load 2D CNN backbone
        if backbone == 'resnet50':
            weights = ResNet50_Weights.DEFAULT if pretrained else None
            base_model = models.resnet50(weights=weights)
            self.feature_dim = 2048
        elif backbone == 'resnet18':
            weights = ResNet18_Weights.DEFAULT if pretrained else None
            base_model = models.resnet18(weights=weights)
            self.feature_dim = 512
        else:
            raise ValueError(f"Unsupported backbone: {backbone}")
        
        # Remove the final FC layer
        self.backbone = nn.Sequential(*list(base_model.children())[:-2])
        self.spatial_pool = nn.AdaptiveAvgPool2d((1, 1))
        
        # LSTM for temporal modeling
        self.lstm = nn.LSTM(
            input_size=self.feature_dim,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=True
        )
        
        # Classifier
        lstm_output_size = hidden_size * 2  # bidirectional
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(lstm_output_size, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x):
        """
        Args:
            x: Input tensor of shape (B, T, C, H, W)
        
        Returns:
            logits: Output tensor of shape (B, num_classes)
        """
        batch_size, num_frames, C, H, W = x.shape
        
        # Reshape to process all frames: (B*T, C, H, W)
        x = x.view(batch_size * num_frames, C, H, W)
        
        # Extract spatial features
        features = self.backbone(x)  # (B*T, feature_dim, h, w)
        features = self.spatial_pool(features)  # (B*T, feature_dim, 1, 1)
        features = features.view(batch_size, num_frames, self.feature_dim)  # (B, T, feature_dim)
        
        # LSTM temporal modeling
        lstm_out, _ = self.lstm(features)  # (B, T, hidden_size*2)
        
        # Use the last timestep output
        final_features = lstm_out[:, -1, :]  # (B, hidden_size*2)
        
        # Classification
        logits = self.classifier(final_features)  # (B, num_classes)
        
        return logits


class SimpleC3D(nn.Module):
    """
    Simplified 3D CNN for video action recognition
    Processes the entire video clip as a 3D tensor
    """
    
    def __init__(self, num_classes, num_frames=16, dropout=0.5):
        super(SimpleC3D, self).__init__()
        
        # 3D Convolutional layers
        self.conv1 = nn.Sequential(
            nn.Conv3d(3, 64, kernel_size=3, padding=1),
            nn.BatchNorm3d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool3d(kernel_size=(1, 2, 2), stride=(1, 2, 2))
        )
        
        self.conv2 = nn.Sequential(
            nn.Conv3d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm3d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool3d(kernel_size=(2, 2, 2), stride=(2, 2, 2))
        )
        
        self.conv3 = nn.Sequential(
            nn.Conv3d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm3d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool3d(kernel_size=(2, 2, 2), stride=(2, 2, 2))
        )
        
        self.conv4 = nn.Sequential(
            nn.Conv3d(256, 256, kernel_size=3, padding=1),
            nn.BatchNorm3d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool3d(kernel_size=(2, 2, 2), stride=(2, 2, 2))
        )
        
        # Global pooling
        self.global_pool = nn.AdaptiveAvgPool3d((1, 1, 1))
        
        # Classifier
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(256, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(128, num_classes)
        )
    
    def forward(self, x):
        """
        Args:
            x: Input tensor of shape (B, T, C, H, W)
        
        Returns:
            logits: Output tensor of shape (B, num_classes)
        """
        # Rearrange to (B, C, T, H, W) for 3D convolution
        x = x.permute(0, 2, 1, 3, 4)
        
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x = self.conv4(x)
        
        x = self.global_pool(x)
        x = x.view(x.size(0), -1)
        
        logits = self.classifier(x)
        
        return logits


def create_model(config):
    """
    Factory function to create model based on configuration
    """
    model_config = config['model']
    architecture = model_config['architecture']
    
    if architecture == 'video_action_detector':
        model = VideoActionDetector(
            num_classes=model_config['num_classes'],
            backbone=model_config['backbone'],
            num_frames=model_config['num_frames'],
            dropout=model_config['dropout'],
            pretrained=model_config['pretrained']
        )
    elif architecture == 'lstm':
        model = LSTMActionDetector(
            num_classes=model_config['num_classes'],
            backbone=model_config['backbone'],
            num_frames=model_config['num_frames'],
            dropout=model_config['dropout'],
            pretrained=model_config['pretrained']
        )
    elif architecture == 'c3d':
        model = SimpleC3D(
            num_classes=model_config['num_classes'],
            num_frames=model_config['num_frames'],
            dropout=model_config['dropout']
        )
    else:
        raise ValueError(f"Unknown architecture: {architecture}")
    
    return model

