"""
Training script for unsafe behavior detection using Label Studio annotations.

This script trains a video classification model to detect safety violations
such as missing PPE (gloves, helmet, etc.) and other unsafe behaviors.

Usage:
    python train_safety_model.py --json path/to/labelstudio_export.json
    python train_safety_model.py  # Uses default path
"""
import os
import sys
import yaml
import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm
import numpy as np
from pathlib import Path
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
from datetime import datetime

from models.action_detector import create_model
from data.labelstudio_dataset import LabelStudioVideoDataset, create_labelstudio_dataloaders
from utils.logger import setup_logger


class SafetyModelTrainer:
    """
    Trainer for safety violation detection model using Label Studio annotations.
    """
    
    def __init__(self, config: dict, labelstudio_json_path: str):
        self.config = config
        self.labelstudio_json_path = labelstudio_json_path
        
        # Setup device
        self.device = torch.device(
            config['training']['device'] if torch.cuda.is_available() else 'cpu'
        )
        
        # Setup directories
        self.setup_directories()
        
        # Setup logger
        self.logger = setup_logger(config['logging']['save_dir'])
        self.logger.info(f"Using device: {self.device}")
        self.logger.info(f"Label Studio export: {labelstudio_json_path}")
        
        # Create dataloaders
        self.train_loader, self.val_loader = self.create_dataloaders()
        
        # Determine number of classes from dataset
        sample_dataset = self.train_loader.dataset
        if hasattr(sample_dataset, 'get_num_classes'):
            num_classes = sample_dataset.get_num_classes()
        else:
            # Count unique labels
            labels = set()
            for sample in sample_dataset.samples:
                labels.add(sample['label_id'])
            num_classes = max(labels) + 1
        
        self.logger.info(f"Number of classes: {num_classes}")
        
        # Update config with actual number of classes
        config['model']['num_classes'] = num_classes
        
        # Create model
        self.model = create_model(config).to(self.device)
        self.logger.info(f"Model: {config['model']['architecture']}")
        self.logger.info(f"Parameters: {self.count_parameters():,}")
        
        # Compute class weights for imbalanced data
        class_weights = self.compute_class_weights()
        if class_weights is not None:
            class_weights = class_weights.to(self.device)
            self.criterion = nn.CrossEntropyLoss(weight=class_weights)
            self.logger.info(f"Using weighted loss for imbalanced classes")
        else:
            self.criterion = nn.CrossEntropyLoss()
        
        # Optimizer
        self.optimizer = self.create_optimizer()
        
        # Scheduler
        self.scheduler = self.create_scheduler()
        
        # Tensorboard
        if config['logging']['tensorboard']:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            tb_dir = os.path.join(config['logging']['tensorboard_dir'], f'safety_model_{timestamp}')
            self.writer = SummaryWriter(log_dir=tb_dir)
        else:
            self.writer = None
        
        # Training state
        self.current_epoch = 0
        self.best_val_f1 = 0.0
        self.global_step = 0
        
        # Store label mapping for later use
        self.label_mapping = sample_dataset.label_mapping if hasattr(sample_dataset, 'label_mapping') else {}
    
    def setup_directories(self):
        """Create necessary directories."""
        dirs = [
            self.config['logging']['save_dir'],
            self.config['checkpointing']['save_dir'],
        ]
        if self.config['logging']['tensorboard']:
            dirs.append(self.config['logging']['tensorboard_dir'])
        
        for d in dirs:
            Path(d).mkdir(parents=True, exist_ok=True)
    
    def create_dataloaders(self):
        """Create train and validation dataloaders."""
        model_config = self.config['model']
        training_config = self.config['training']
        
        return create_labelstudio_dataloaders(
            labelstudio_json_path=self.labelstudio_json_path,
            batch_size=training_config['batch_size'],
            num_workers=training_config['num_workers'],
            num_frames=model_config['num_frames'],
            frame_interval=model_config['frame_interval'],
            input_size=tuple(model_config['input_size']),
            train_split=0.8,
            include_safe_segments=True
        )
    
    def compute_class_weights(self) -> torch.Tensor:
        """Compute class weights for imbalanced dataset."""
        label_counts = {}
        
        dataset = self.train_loader.dataset
        for sample in dataset.samples:
            label_id = sample['label_id']
            label_counts[label_id] = label_counts.get(label_id, 0) + 1
        
        if not label_counts:
            return None
        
        # Compute inverse frequency weights
        total = sum(label_counts.values())
        num_classes = max(label_counts.keys()) + 1
        weights = torch.zeros(num_classes)
        
        for label_id, count in label_counts.items():
            weights[label_id] = total / (num_classes * count)
        
        # Normalize weights
        weights = weights / weights.sum() * num_classes
        
        self.logger.info(f"Class weights: {weights.tolist()}")
        return weights
    
    def count_parameters(self) -> int:
        """Count trainable parameters."""
        return sum(p.numel() for p in self.model.parameters() if p.requires_grad)
    
    def create_optimizer(self):
        """Create optimizer."""
        opt_name = self.config['training']['optimizer'].lower()
        lr = self.config['training']['learning_rate']
        wd = self.config['training']['weight_decay']
        
        if opt_name == 'adam':
            return optim.Adam(self.model.parameters(), lr=lr, weight_decay=wd)
        elif opt_name == 'adamw':
            return optim.AdamW(self.model.parameters(), lr=lr, weight_decay=wd)
        elif opt_name == 'sgd':
            return optim.SGD(self.model.parameters(), lr=lr, weight_decay=wd, momentum=0.9)
        else:
            raise ValueError(f"Unknown optimizer: {opt_name}")
    
    def create_scheduler(self):
        """Create learning rate scheduler."""
        sched_name = self.config['training']['scheduler'].lower()
        num_epochs = self.config['training']['num_epochs']
        
        if sched_name == 'cosine':
            return optim.lr_scheduler.CosineAnnealingLR(self.optimizer, T_max=num_epochs)
        elif sched_name == 'step':
            return optim.lr_scheduler.StepLR(self.optimizer, step_size=10, gamma=0.1)
        elif sched_name == 'plateau':
            return optim.lr_scheduler.ReduceLROnPlateau(self.optimizer, mode='max', patience=5)
        else:
            raise ValueError(f"Unknown scheduler: {sched_name}")
    
    def train_epoch(self) -> dict:
        """Train for one epoch."""
        self.model.train()
        epoch_loss = 0.0
        all_preds = []
        all_labels = []
        
        pbar = tqdm(self.train_loader, desc=f"Epoch {self.current_epoch+1} [Train]")
        
        for batch_idx, (videos, labels) in enumerate(pbar):
            videos = videos.to(self.device)
            labels = labels.to(self.device)
            
            # Forward
            self.optimizer.zero_grad()
            outputs = self.model(videos)
            loss = self.criterion(outputs, labels)
            
            # Backward
            loss.backward()
            
            # Gradient clipping
            if self.config['training']['gradient_clip'] > 0:
                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(),
                    self.config['training']['gradient_clip']
                )
            
            self.optimizer.step()
            
            # Track metrics
            epoch_loss += loss.item()
            preds = torch.argmax(outputs, dim=1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            
            pbar.set_postfix({'loss': f'{loss.item():.4f}'})
            
            if self.writer:
                self.writer.add_scalar('train/batch_loss', loss.item(), self.global_step)
            
            self.global_step += 1
        
        # Calculate metrics
        avg_loss = epoch_loss / len(self.train_loader)
        accuracy = accuracy_score(all_labels, all_preds)
        precision, recall, f1, _ = precision_recall_fscore_support(
            all_labels, all_preds, average='weighted', zero_division=0
        )
        
        return {
            'loss': avg_loss,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1
        }
    
    def validate(self) -> dict:
        """Validate the model."""
        self.model.eval()
        epoch_loss = 0.0
        all_preds = []
        all_labels = []
        
        with torch.no_grad():
            pbar = tqdm(self.val_loader, desc=f"Epoch {self.current_epoch+1} [Val]")
            
            for videos, labels in pbar:
                videos = videos.to(self.device)
                labels = labels.to(self.device)
                
                outputs = self.model(videos)
                loss = self.criterion(outputs, labels)
                
                epoch_loss += loss.item()
                preds = torch.argmax(outputs, dim=1)
                all_preds.extend(preds.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
                
                pbar.set_postfix({'loss': f'{loss.item():.4f}'})
        
        avg_loss = epoch_loss / len(self.val_loader)
        accuracy = accuracy_score(all_labels, all_preds)
        precision, recall, f1, _ = precision_recall_fscore_support(
            all_labels, all_preds, average='weighted', zero_division=0
        )
        
        return {
            'loss': avg_loss,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'predictions': all_preds,
            'labels': all_labels
        }
    
    def save_checkpoint(self, is_best: bool = False):
        """Save model checkpoint."""
        checkpoint = {
            'epoch': self.current_epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'best_val_f1': self.best_val_f1,
            'config': self.config,
            'label_mapping': self.label_mapping
        }
        
        save_dir = Path(self.config['checkpointing']['save_dir'])
        
        # Save latest
        latest_path = save_dir / 'safety_model_latest.pth'
        torch.save(checkpoint, latest_path)
        
        # Save best
        if is_best:
            best_path = save_dir / 'safety_model_best.pth'
            torch.save(checkpoint, best_path)
            self.logger.info(f"Saved best model: {best_path}")
    
    def train(self):
        """Main training loop."""
        self.logger.info("=" * 60)
        self.logger.info("STARTING SAFETY MODEL TRAINING")
        self.logger.info("=" * 60)
        self.logger.info(f"Train samples: {len(self.train_loader.dataset)}")
        self.logger.info(f"Val samples: {len(self.val_loader.dataset)}")
        
        num_epochs = self.config['training']['num_epochs']
        
        for epoch in range(num_epochs):
            self.current_epoch = epoch
            
            # Train
            train_metrics = self.train_epoch()
            
            # Validate
            val_metrics = self.validate()
            
            # Update scheduler
            if isinstance(self.scheduler, optim.lr_scheduler.ReduceLROnPlateau):
                self.scheduler.step(val_metrics['f1'])
            else:
                self.scheduler.step()
            
            # Log
            self.logger.info(
                f"Epoch {epoch+1}/{num_epochs} | "
                f"Train Loss: {train_metrics['loss']:.4f}, Acc: {train_metrics['accuracy']:.4f}, F1: {train_metrics['f1']:.4f} | "
                f"Val Loss: {val_metrics['loss']:.4f}, Acc: {val_metrics['accuracy']:.4f}, F1: {val_metrics['f1']:.4f}"
            )
            
            # Tensorboard
            if self.writer:
                for k, v in train_metrics.items():
                    self.writer.add_scalar(f'train/{k}', v, epoch)
                for k, v in val_metrics.items():
                    if k not in ['predictions', 'labels']:
                        self.writer.add_scalar(f'val/{k}', v, epoch)
            
            # Save checkpoint
            is_best = val_metrics['f1'] > self.best_val_f1
            if is_best:
                self.best_val_f1 = val_metrics['f1']
            
            if (epoch + 1) % self.config['logging']['save_frequency'] == 0 or is_best:
                self.save_checkpoint(is_best=is_best)
        
        # Final summary
        self.logger.info("=" * 60)
        self.logger.info("TRAINING COMPLETE")
        self.logger.info(f"Best validation F1: {self.best_val_f1:.4f}")
        self.logger.info("=" * 60)
        
        # Print classification report
        if val_metrics['predictions'] and val_metrics['labels']:
            # Get label names
            id_to_label = {v: k for k, v in self.label_mapping.items()}
            unique_labels = sorted(set(val_metrics['labels']))
            target_names = [id_to_label.get(l, f'Class_{l}') for l in unique_labels]
            
            print("\nClassification Report:")
            print(classification_report(
                val_metrics['labels'],
                val_metrics['predictions'],
                labels=unique_labels,
                target_names=target_names,
                zero_division=0
            ))
        
        if self.writer:
            self.writer.close()


def main():
    parser = argparse.ArgumentParser(description='Train safety violation detection model')
    parser.add_argument(
        '--json', '-j', type=str,
        default=r'C:\Users\yousi\Downloads\project-1-at-2025-12-17-13-45-ec1123a5.json',
        help='Path to Label Studio JSON export'
    )
    parser.add_argument(
        '--config', '-c', type=str,
        default='config.yaml',
        help='Path to config file'
    )
    parser.add_argument(
        '--epochs', '-e', type=int, default=None,
        help='Override number of epochs'
    )
    parser.add_argument(
        '--batch-size', '-b', type=int, default=None,
        help='Override batch size'
    )
    
    args = parser.parse_args()
    
    # Load config
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
    
    # Override config if specified
    if args.epochs:
        config['training']['num_epochs'] = args.epochs
    if args.batch_size:
        config['training']['batch_size'] = args.batch_size
    
    # Check if JSON file exists
    if not os.path.exists(args.json):
        print(f"Error: Label Studio export not found: {args.json}")
        sys.exit(1)
    
    # Create trainer and start training
    trainer = SafetyModelTrainer(config, args.json)
    trainer.train()


if __name__ == '__main__':
    main()



