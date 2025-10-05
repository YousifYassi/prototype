"""
Evaluation script for unsafe action detection model
"""
import os
import yaml
import torch
import argparse
import numpy as np
from tqdm import tqdm
from pathlib import Path

from models.action_detector import create_model
from data.dataset import BDD100KActionDataset
from torch.utils.data import DataLoader
from utils.metrics import calculate_metrics, print_metrics
from utils.visualization import plot_confusion_matrix
from utils.logger import setup_logger


def evaluate(config, model_path, split='test'):
    """
    Evaluate model on test set
    
    Args:
        config: Configuration dictionary
        model_path: Path to model checkpoint
        split: Dataset split to evaluate ('test', 'val', or 'train')
    """
    device = torch.device(config['training']['device'] 
                         if torch.cuda.is_available() else 'cpu')
    
    # Setup logger
    logger = setup_logger(config['logging']['save_dir'])
    logger.info(f"Evaluating model on {split} set")
    logger.info(f"Device: {device}")
    
    # Load model
    model = create_model(config).to(device)
    checkpoint = torch.load(model_path, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    logger.info(f"Loaded model from: {model_path}")
    
    # Create dataset
    dataset = BDD100KActionDataset(
        root_dir=config['dataset']['root_dir'],
        annotations_file=config['dataset']['annotations_file'],
        split=split,
        num_frames=config['model']['num_frames'],
        frame_interval=config['model']['frame_interval'],
        input_size=tuple(config['model']['input_size']),
        augment=False
    )
    
    dataloader = DataLoader(
        dataset,
        batch_size=config['training']['batch_size'],
        shuffle=False,
        num_workers=config['training']['num_workers'],
        pin_memory=True
    )
    
    logger.info(f"Dataset size: {len(dataset)}")
    
    # Evaluation
    all_preds = []
    all_labels = []
    all_probs = []
    
    with torch.no_grad():
        for videos, labels in tqdm(dataloader, desc='Evaluating'):
            videos = videos.to(device)
            labels = labels.to(device)
            
            outputs = model(videos)
            probs = torch.softmax(outputs, dim=1)
            preds = torch.argmax(outputs, dim=1)
            
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())
    
    # Calculate metrics
    class_names = ['safe'] + config['unsafe_actions']
    metrics = calculate_metrics(all_labels, all_preds, class_names)
    
    # Print metrics
    print_metrics(metrics, logger)
    
    # Plot confusion matrix
    output_dir = Path('output') / 'evaluation'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    cm_path = output_dir / f'confusion_matrix_{split}.png'
    plot_confusion_matrix(metrics['confusion_matrix'], class_names, save_path=cm_path)
    logger.info(f"Confusion matrix saved to: {cm_path}")
    
    # Save detailed results
    results = {
        'metrics': {
            'accuracy': float(metrics['accuracy']),
            'precision': float(metrics['precision_weighted']),
            'recall': float(metrics['recall_weighted']),
            'f1': float(metrics['f1_weighted']),
        },
        'per_class_metrics': {
            class_names[i]: {
                'precision': float(metrics['per_class_precision'][i]),
                'recall': float(metrics['per_class_recall'][i]),
                'f1': float(metrics['per_class_f1'][i]),
                'support': int(metrics['per_class_support'][i])
            }
            for i in range(len(class_names))
        }
    }
    
    import json
    results_path = output_dir / f'results_{split}.json'
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Results saved to: {results_path}")
    
    return metrics


def main():
    parser = argparse.ArgumentParser(description='Evaluate unsafe action detection model')
    parser.add_argument('--config', type=str, default='config.yaml',
                       help='Path to configuration file')
    parser.add_argument('--model', type=str, default='checkpoints/best_model.pth',
                       help='Path to model checkpoint')
    parser.add_argument('--split', type=str, default='test',
                       choices=['train', 'val', 'test'],
                       help='Dataset split to evaluate')
    
    args = parser.parse_args()
    
    # Load config
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
    
    # Evaluate
    evaluate(config, args.model, args.split)


if __name__ == '__main__':
    main()

