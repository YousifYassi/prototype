"""
Model Registry System for Jurisdiction and Industry-Specific Models
Handles loading and fallback logic for specialized models
"""
import os
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ModelRegistry:
    """
    Manages model loading with jurisdiction/industry-specific fallback logic
    """
    
    def __init__(self, base_checkpoint_dir: str = "checkpoints"):
        self.base_checkpoint_dir = Path(base_checkpoint_dir)
        # Use safety model trained with Label Studio annotations as the default
        self.safety_model_path = self.base_checkpoint_dir / "safety_model_best.pth"
        self.legacy_model_path = self.base_checkpoint_dir / "best_model.pth"
        
        # Cache loaded model paths to avoid redundant checks
        self._model_cache = {}
    
    def get_model_path(
        self, 
        jurisdiction_code: Optional[str] = None,
        industry_code: Optional[str] = None,
        custom_path: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Get the appropriate model path based on jurisdiction and industry.
        
        Priority:
        1. Custom model path (if provided)
        2. Jurisdiction + Industry specific model
        3. Industry-only specific model
        4. Jurisdiction-only specific model
        5. Generic model (fallback)
        
        Args:
            jurisdiction_code: Code for jurisdiction (e.g., "ontario")
            industry_code: Code for industry (e.g., "food_safety")
            custom_path: Custom model path override
        
        Returns:
            Tuple of (model_path, model_type)
            model_type: "custom", "jurisdiction_industry", "industry", "jurisdiction", or "generic"
        """
        
        # Priority 1: Custom model path
        if custom_path:
            custom_model = Path(custom_path)
            if custom_model.exists():
                logger.info(f"Using custom model: {custom_path}")
                return str(custom_model), "custom"
            else:
                logger.warning(f"Custom model path does not exist: {custom_path}, falling back")
        
        # Priority 2: Jurisdiction + Industry specific model
        if jurisdiction_code and industry_code:
            cache_key = f"{jurisdiction_code}_{industry_code}"
            
            if cache_key in self._model_cache:
                return self._model_cache[cache_key]
            
            combined_model = self.base_checkpoint_dir / f"{jurisdiction_code}_{industry_code}_model.pth"
            if combined_model.exists():
                logger.info(f"Using jurisdiction+industry model: {combined_model}")
                result = (str(combined_model), "jurisdiction_industry")
                self._model_cache[cache_key] = result
                return result
        
        # Priority 3: Industry-only specific model
        if industry_code:
            cache_key = f"industry_{industry_code}"
            
            if cache_key in self._model_cache:
                return self._model_cache[cache_key]
            
            industry_model = self.base_checkpoint_dir / f"industry_{industry_code}_model.pth"
            if industry_model.exists():
                logger.info(f"Using industry-specific model: {industry_model}")
                result = (str(industry_model), "industry")
                self._model_cache[cache_key] = result
                return result
        
        # Priority 4: Jurisdiction-only specific model
        if jurisdiction_code:
            cache_key = f"jurisdiction_{jurisdiction_code}"
            
            if cache_key in self._model_cache:
                return self._model_cache[cache_key]
            
            jurisdiction_model = self.base_checkpoint_dir / f"jurisdiction_{jurisdiction_code}_model.pth"
            if jurisdiction_model.exists():
                logger.info(f"Using jurisdiction-specific model: {jurisdiction_model}")
                result = (str(jurisdiction_model), "jurisdiction")
                self._model_cache[cache_key] = result
                return result
        
        # Priority 5: Generic fallback model (prefer safety model over legacy)
        if self.safety_model_path.exists():
            logger.info(f"Using safety model (Label Studio trained): {self.safety_model_path}")
            return str(self.safety_model_path), "generic"
        
        if self.legacy_model_path.exists():
            logger.info(f"Using legacy fallback model: {self.legacy_model_path}")
            return str(self.legacy_model_path), "generic"
        
        raise FileNotFoundError(
            f"No model found. Checked: {self.safety_model_path}, {self.legacy_model_path}. "
            "Please train a model first using train_safety_model.py"
        )
    
    def list_available_models(self) -> dict:
        """
        List all available models in the checkpoint directory
        
        Returns:
            Dictionary with model types and their paths
        """
        models = {
            "generic": None,
            "safety_model": None,
            "jurisdiction_industry": [],
            "industry": [],
            "jurisdiction": [],
            "other": []
        }
        
        if self.safety_model_path.exists():
            models["safety_model"] = str(self.safety_model_path)
            models["generic"] = str(self.safety_model_path)  # Safety model is the default
        elif self.legacy_model_path.exists():
            models["generic"] = str(self.legacy_model_path)
        
        # Scan checkpoint directory for models
        if self.base_checkpoint_dir.exists():
            for model_file in self.base_checkpoint_dir.glob("*.pth"):
                model_name = model_file.stem
                
                if model_name in ["best_model", "safety_model_best", "safety_model_latest"]:
                    continue  # Already handled
                
                # Check pattern
                if "_" in model_name and model_name.endswith("_model"):
                    parts = model_name.replace("_model", "").split("_")
                    
                    if len(parts) == 2:
                        # Could be jurisdiction_industry or type_name
                        if parts[0] in ["industry", "jurisdiction"]:
                            models[parts[0]].append(str(model_file))
                        else:
                            # Assume jurisdiction_industry
                            models["jurisdiction_industry"].append(str(model_file))
                    elif len(parts) == 3 and parts[0] in ["industry", "jurisdiction"]:
                        models[parts[0]].append(str(model_file))
                    else:
                        models["other"].append(str(model_file))
                else:
                    models["other"].append(str(model_file))
        
        return models
    
    def validate_model_compatibility(self, model_path: str, expected_num_classes: int) -> bool:
        """
        Validate that a model is compatible with the expected configuration
        
        Args:
            model_path: Path to the model file
            expected_num_classes: Expected number of output classes
        
        Returns:
            True if compatible, False otherwise
        """
        import torch
        
        try:
            checkpoint = torch.load(model_path, map_location='cpu')
            
            # Check if checkpoint has model state
            if 'model_state_dict' in checkpoint:
                state_dict = checkpoint['model_state_dict']
            else:
                state_dict = checkpoint
            
            # Check classifier output dimension
            # Look for the final linear layer
            classifier_keys = [k for k in state_dict.keys() if 'classifier' in k and 'weight' in k]
            
            if classifier_keys:
                last_layer_key = sorted(classifier_keys)[-1]
                output_dim = state_dict[last_layer_key].shape[0]
                
                if output_dim != expected_num_classes:
                    logger.warning(
                        f"Model output dimension ({output_dim}) does not match "
                        f"expected classes ({expected_num_classes})"
                    )
                    return False
            
            return True
        
        except Exception as e:
            logger.error(f"Error validating model {model_path}: {e}")
            return False


# Global registry instance
_registry = None


def get_model_registry(checkpoint_dir: str = "checkpoints") -> ModelRegistry:
    """
    Get the global model registry instance (singleton)
    
    Args:
        checkpoint_dir: Base directory for model checkpoints
    
    Returns:
        ModelRegistry instance
    """
    global _registry
    if _registry is None:
        _registry = ModelRegistry(checkpoint_dir)
    return _registry

