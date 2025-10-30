#!/usr/bin/env python3
"""
Quick CoVLA Setup Test
"""
import os

def test_covla_setup():
    """Test CoVLA dataset setup"""
    print("Testing CoVLA Dataset Setup...")
    print("=" * 40)
    
    # Check authentication
    try:
        from huggingface_hub import whoami
        user_info = whoami()
        print(f"✓ Authenticated as: {user_info['name']}")
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        print("\nTo fix this:")
        print("1. Get your token from: https://huggingface.co/settings/tokens")
        print("2. Set it as environment variable: set HF_TOKEN=your_token")
        print("3. Or run: python -c \"from huggingface_hub import login; login('your_token')\"")
        return False
    
    # Test dataset access
    try:
        from datasets import load_dataset
        print("\nTesting dataset access...")
        
        # Try mini dataset first
        dataset = load_dataset("turing-motors/CoVLA-Dataset-Mini")
        print(f"✓ Successfully loaded CoVLA-Dataset-Mini!")
        print(f"  Available splits: {list(dataset.keys())}")
        
        if 'train' in dataset:
            print(f"  Train samples: {len(dataset['train'])}")
            if len(dataset['train']) > 0:
                sample = dataset['train'][0]
                print(f"  Sample keys: {list(sample.keys())}")
        
        return True
        
    except Exception as e:
        print(f"✗ Dataset access failed: {e}")
        print("\nTo fix this:")
        print("1. Make sure you accepted the license terms")
        print("2. Visit: https://huggingface.co/datasets/turing-motors/CoVLA-Dataset")
        print("3. Click 'Request access' and accept the terms")
        return False

if __name__ == '__main__':
    if test_covla_setup():
        print("\n🎉 CoVLA setup is working correctly!")
        print("\nYou can now:")
        print("1. Run: python test_covla_dataset.py")
        print("2. Run: python train.py")
    else:
        print("\n❌ CoVLA setup needs attention.")
        print("Please follow the steps above to complete authentication.")

