"""
Training script for unsafe action detection model
"""
import os
import sys
import yaml
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm
import numpy as np
from pathlib import Path
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix

from models.action_detector import create_model
from data.dataset import create_dataloaders
from utils.metrics import calculate_metrics
from utils.logger import setup_logger


class Trainer:
    """
    Trainer class for unsafe action detection
    """
    
    def __init__(self, config):
        self.config = config
        self.device = torch.device(config['training']['device'] 
                                   if torch.cuda.is_available() else 'cpu')
        
        # Setup directories
        self.setup_directories()
        
        # Setup logger
        self.logger = setup_logger(config['logging']['save_dir'])
        self.logger.info(f"Using device: {self.device}")
        
        # Create model
        self.model = create_model(config).to(self.device)
        self.logger.info(f"Model created: {config['model']['architecture']}")
        self.logger.info(f"Number of parameters: {self.count_parameters()}")
        
        # Create dataloaders
        self.train_loader, self.val_loader = create_dataloaders(config)
        self.logger.info(f"Train samples: {len(self.train_loader.dataset)}")
        self.logger.info(f"Val samples: {len(self.val_loader.dataset)}")
        
        # Loss function (with class weights for imbalanced data)
        self.criterion = nn.CrossEntropyLoss()
        
        # Optimizer
        self.optimizer = self.create_optimizer()
        
        # Learning rate scheduler
        self.scheduler = self.create_scheduler()
        
        # Tensorboard
        if config['logging']['tensorboard']:
            self.writer = SummaryWriter(log_dir=config['logging']['tensorboard_dir'])
        else:
            self.writer = None
        
        # Training state
        self.current_epoch = 0
        self.best_val_acc = 0.0
        self.global_step = 0
    
    def setup_directories(self):
        """Create necessary directories"""
        dirs = [
            self.config['logging']['save_dir'],
            self.config['checkpointing']['save_dir'],
        ]
        if self.config['logging']['tensorboard']:
            dirs.append(self.config['logging']['tensorboard_dir'])
        
        for directory in dirs:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def count_parameters(self):
        """Count trainable parameters"""
        return sum(p.numel() for p in self.model.parameters() if p.requires_grad)
    
    def create_optimizer(self):
        """Create optimizer"""
        optimizer_name = self.config['training']['optimizer'].lower()
        lr = self.config['training']['learning_rate']
        weight_decay = self.config['training']['weight_decay']
        
        if optimizer_name == 'adam':
            optimizer = optim.Adam(self.model.parameters(), lr=lr, weight_decay=weight_decay)
        elif optimizer_name == 'adamw':
            optimizer = optim.AdamW(self.model.parameters(), lr=lr, weight_decay=weight_decay)
        elif optimizer_name == 'sgd':
            optimizer = optim.SGD(self.model.parameters(), lr=lr, 
                                 weight_decay=weight_decay, momentum=0.9)
        else:
            raise ValueError(f"Unknown optimizer: {optimizer_name}")
        
        return optimizer
    
    def create_scheduler(self):
        """Create learning rate scheduler"""
        scheduler_name = self.config['training']['scheduler'].lower()
        num_epochs = self.config['training']['num_epochs']
        
        if scheduler_name == 'cosine':
            scheduler = optim.lr_scheduler.CosineAnnealingLR(self.optimizer, T_max=num_epochs)
        elif scheduler_name == 'step':
            scheduler = optim.lr_scheduler.StepLR(self.optimizer, step_size=10, gamma=0.1)
        elif scheduler_name == 'plateau':
            scheduler = optim.lr_scheduler.ReduceLROnPlateau(self.optimizer, mode='max', 
                                                             patience=5, factor=0.5)
        else:
            raise ValueError(f"Unknown scheduler: {scheduler_name}")
        
        return scheduler
    
    def train_epoch(self):
        """Train for one epoch"""
        self.model.train()
        epoch_loss = 0.0
        all_preds = []
        all_labels = []
        
        pbar = tqdm(self.train_loader, desc=f"Epoch {self.current_epoch+1} [Train]")
        
        for batch_idx, (videos, labels) in enumerate(pbar):
            videos = videos.to(self.device)
            labels = labels.to(self.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            outputs = self.model(videos)
            loss = self.criterion(outputs, labels)
            
            # Backward pass
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
            
            # Update progress bar
            pbar.set_postfix({'loss': loss.item()})
            
            # Log to tensorboard
            if self.writer:
                self.writer.add_scalar('train/batch_loss', loss.item(), self.global_step)
                self.writer.add_scalar('train/learning_rate', 
                                     self.optimizer.param_groups[0]['lr'], 
                                     self.global_step)
            
            self.global_step += 1
        
        # Calculate epoch metrics
        avg_loss = epoch_loss / len(self.train_loader)
        accuracy = accuracy_score(all_labels, all_preds)
        precision, recall, f1, _ = precision_recall_fscore_support(
            all_labels, all_preds, average='weighted', zero_division=0
        )
        
        metrics = {
            'loss': avg_loss,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1
        }
        
        return metrics
    
    def validate(self):
        """Validate the model"""
        self.model.eval()
        epoch_loss = 0.0
        all_preds = []
        all_labels = []
        
        with torch.no_grad():
            pbar = tqdm(self.val_loader, desc=f"Epoch {self.current_epoch+1} [Val]")
            
            for videos, labels in pbar:
                videos = videos.to(self.device)
                labels = labels.to(self.device)
                
                # Forward pass
                outputs = self.model(videos)
                loss = self.criterion(outputs, labels)
                
                # Track metrics
                epoch_loss += loss.item()
                preds = torch.argmax(outputs, dim=1)
                all_preds.extend(preds.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
                
                pbar.set_postfix({'loss': loss.item()})
        
        # Calculate metrics
        avg_loss = epoch_loss / len(self.val_loader)
        accuracy = accuracy_score(all_labels, all_preds)
        precision, recall, f1, _ = precision_recall_fscore_support(
            all_labels, all_preds, average='weighted', zero_division=0
        )
        
        metrics = {
            'loss': avg_loss,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'predictions': all_preds,
            'labels': all_labels
        }
        
        return metrics
    
    def save_checkpoint(self, is_best=False):
        """Save model checkpoint"""
        checkpoint = {
            'epoch': self.current_epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'best_val_acc': self.best_val_acc,
            'config': self.config
        }
        
        save_dir = Path(self.config['checkpointing']['save_dir'])
        
        # Save latest checkpoint
        checkpoint_path = save_dir / f'checkpoint_epoch_{self.current_epoch}.pth'
        torch.save(checkpoint, checkpoint_path)
        self.logger.info(f"Saved checkpoint: {checkpoint_path}")
        
        # Save best checkpoint
        if is_best:
            best_path = save_dir / 'best_model.pth'
            torch.save(checkpoint, best_path)
            self.logger.info(f"Saved best model: {best_path}")
    
    def train(self):
        """Main training loop"""
        self.logger.info("Starting training...")
        num_epochs = self.config['training']['num_epochs']
        
        for epoch in range(num_epochs):
            self.current_epoch = epoch
            
            # Train
            train_metrics = self.train_epoch()
            
            # Validate
            val_metrics = self.validate()
            
            # Update learning rate
            if isinstance(self.scheduler, optim.lr_scheduler.ReduceLROnPlateau):
                self.scheduler.step(val_metrics['accuracy'])
            else:
                self.scheduler.step()
            
            # Log metrics
            self.logger.info(
                f"Epoch {epoch+1}/{num_epochs} - "
                f"Train Loss: {train_metrics['loss']:.4f}, "
                f"Train Acc: {train_metrics['accuracy']:.4f}, "
                f"Val Loss: {val_metrics['loss']:.4f}, "
                f"Val Acc: {val_metrics['accuracy']:.4f}, "
                f"Val F1: {val_metrics['f1']:.4f}"
            )
            
            # Tensorboard logging
            if self.writer:
                for key, value in train_metrics.items():
                    if key not in ['predictions', 'labels']:
                        self.writer.add_scalar(f'train/{key}', value, epoch)
                
                for key, value in val_metrics.items():
                    if key not in ['predictions', 'labels']:
                        self.writer.add_scalar(f'val/{key}', value, epoch)
            
            # Save checkpoint
            is_best = val_metrics['accuracy'] > self.best_val_acc
            if is_best:
                self.best_val_acc = val_metrics['accuracy']
            
            save_freq = self.config['logging']['save_frequency']
            if (epoch + 1) % save_freq == 0 or is_best:
                self.save_checkpoint(is_best=is_best)
        
        self.logger.info(f"Training completed! Best validation accuracy: {self.best_val_acc:.4f}")
        
        if self.writer:
            self.writer.close()


def main():
    # Load configuration
    config_path = 'config.yaml'
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Create trainer and start training
    trainer = Trainer(config)
    trainer.train()


if __name__ == '__main__':
    main()

