"""
Metrics calculation utilities
"""
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    confusion_matrix, classification_report
)


def calculate_metrics(y_true, y_pred, class_names=None):
    """
    Calculate comprehensive metrics for multi-class classification
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        class_names: List of class names (optional)
    
    Returns:
        metrics: Dictionary of metrics
    """
    # Basic metrics
    accuracy = accuracy_score(y_true, y_pred)
    
    # Per-class metrics
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, average=None, zero_division=0
    )
    
    # Weighted average metrics
    precision_avg, recall_avg, f1_avg, _ = precision_recall_fscore_support(
        y_true, y_pred, average='weighted', zero_division=0
    )
    
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    
    metrics = {
        'accuracy': accuracy,
        'precision_weighted': precision_avg,
        'recall_weighted': recall_avg,
        'f1_weighted': f1_avg,
        'per_class_precision': precision,
        'per_class_recall': recall,
        'per_class_f1': f1,
        'per_class_support': support,
        'confusion_matrix': cm
    }
    
    # Classification report
    if class_names:
        report = classification_report(y_true, y_pred, 
                                      target_names=class_names,
                                      zero_division=0)
        metrics['classification_report'] = report
    
    return metrics


def print_metrics(metrics, logger=None):
    """
    Print metrics in a formatted way
    
    Args:
        metrics: Dictionary of metrics
        logger: Logger instance (optional)
    """
    output = []
    
    output.append("=" * 50)
    output.append("Evaluation Metrics")
    output.append("=" * 50)
    output.append(f"Accuracy: {metrics['accuracy']:.4f}")
    output.append(f"Precision (weighted): {metrics['precision_weighted']:.4f}")
    output.append(f"Recall (weighted): {metrics['recall_weighted']:.4f}")
    output.append(f"F1-Score (weighted): {metrics['f1_weighted']:.4f}")
    output.append("")
    
    if 'classification_report' in metrics:
        output.append("Classification Report:")
        output.append(metrics['classification_report'])
    
    output.append("=" * 50)
    
    message = "\n".join(output)
    
    if logger:
        logger.info(message)
    else:
        print(message)

