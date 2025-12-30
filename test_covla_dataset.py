#!/usr/bin/env python3
"""
Test script for CoVLA dataset integration
"""
import yaml
import torch
from data.dataset import CoVLADataset, create_dataloaders
from pathlib import Path

def test_covla_dataset():
    """Test CoVLA dataset loading and basic functionality"""
    print("Testing CoVLA Dataset Integration...")
    print("=" * 50)
    
    try:
        # Test with mini dataset first
        print("1. Testing CoVLA Mini Dataset...")
        dataset = CoVLADataset(
            dataset_name="turing-motors/CoVLA-Dataset-Mini",
            split='train',
            num_frames=8,  # Reduced for testing
            frame_interval=2,
            input_size=(224, 224),
            use_mini=True
        )
        
        print(f"   [OK] Dataset loaded successfully")
        print(f"   [OK] Number of samples: {len(dataset)}")
        
        if len(dataset) > 0:
            # Test loading a sample
            print("2. Testing sample loading...")
            video_tensor, label = dataset[0]
            print(f"   [OK] Video tensor shape: {video_tensor.shape}")
            print(f"   [OK] Label: {label}")
            print(f"   [OK] Expected shape: (num_frames, channels, height, width)")
            
            # Test dataloader creation
            print("3. Testing dataloader creation...")
            dataloader = torch.utils.data.DataLoader(
                dataset, 
                batch_size=2, 
                shuffle=False,
                num_workers=0  # Use 0 for testing
            )
            
            batch = next(iter(dataloader))
            videos, labels = batch
            print(f"   [OK] Batch videos shape: {videos.shape}")
            print(f"   [OK] Batch labels shape: {labels.shape}")
            
        print("\n[OK] CoVLA Dataset integration test PASSED!")
        return True
        
    except Exception as e:
        print(f"\n✗ CoVLA Dataset integration test FAILED!")
        print(f"Error: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure you have accepted the license terms on Hugging Face")
        print("   Visit: https://huggingface.co/datasets/turing-motors/CoVLA-Dataset")
        print("2. Install required packages: pip install datasets huggingface_hub")
        print("3. Authenticate with Hugging Face:")
        print("   - Run: huggingface-cli login")
        print("   - Or set HF_TOKEN environment variable")
        print("4. Check your internet connection")
        print("5. For testing, you can use a mock dataset by setting use_mini=False")
        return False

def test_config_integration():
    """Test integration with config.yaml"""
    print("\nTesting Config Integration...")
    print("=" * 50)
    
    try:
        # Load config
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        print(f"[OK] Config loaded successfully")
        print(f"[OK] Dataset name: {config['dataset']['name']}")
        
        if config['dataset']['name'] == 'covla':
            print("[OK] Using CoVLA dataset configuration")
            
            # Test dataloader creation with config
            print("4. Testing dataloader creation with config...")
            train_loader, val_loader = create_dataloaders(config)
            
            print(f"   [OK] Train loader created: {len(train_loader.dataset)} samples")
            print(f"   [OK] Val loader created: {len(val_loader.dataset)} samples")
            
            print("\n[OK] Config integration test PASSED!")
            return True
        else:
            print("ℹ Config is set to use BDD100K dataset, not CoVLA")
            return True
            
    except Exception as e:
        print(f"\n✗ Config integration test FAILED!")
        print(f"Error: {e}")
        return False

def main():
    """Main test function"""
    print("CoVLA Dataset Integration Test")
    print("=" * 50)
    
    # Test 1: Basic dataset functionality
    test1_passed = test_covla_dataset()
    
    # Test 2: Config integration
    test2_passed = test_config_integration()
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY:")
    print(f"CoVLA Dataset Test: {'PASSED' if test1_passed else 'FAILED'}")
    print(f"Config Integration Test: {'PASSED' if test2_passed else 'FAILED'}")
    
    if test1_passed and test2_passed:
        print("\nAll tests PASSED! CoVLA dataset is ready to use.")
        print("\nNext steps:")
        print("1. Run: python train.py (to start training with CoVLA dataset)")
        print("2. Monitor training progress with TensorBoard")
        print("3. Adjust config.yaml parameters as needed")
    else:
        print("\n[X] Some tests FAILED. Please check the errors above.")
        print("\nTo switch back to BDD100K dataset:")
        print("1. Change 'name: covla' to 'name: bdd100k' in config.yaml")
        print("2. Make sure BDD100K data is in datasets/bdd100k/")

if __name__ == '__main__':
    main()
