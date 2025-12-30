#!/usr/bin/env python3
"""
CoVLA Dataset Authentication Setup Script
"""
import os
import subprocess
import sys

def check_huggingface_auth():
    """Check if user is authenticated with Hugging Face"""
    try:
        from huggingface_hub import whoami
        user_info = whoami()
        print(f"[OK] Authenticated as: {user_info['name']}")
        return True
    except Exception as e:
        print(f"✗ Not authenticated: {e}")
        return False

def setup_authentication():
    """Guide user through authentication setup"""
    print("CoVLA Dataset Authentication Setup")
    print("=" * 50)
    
    print("\n1. First, you need to accept the license terms:")
    print("   Visit: https://huggingface.co/datasets/turing-motors/CoVLA-Dataset")
    print("   Click 'Request access' and accept the license terms")
    
    print("\n2. Create a Hugging Face account if you don't have one:")
    print("   Visit: https://huggingface.co/join")
    
    print("\n3. Get your access token:")
    print("   Visit: https://huggingface.co/settings/tokens")
    print("   Create a new token with 'Read' permissions")
    
    print("\n4. Authenticate using one of these methods:")
    print("\n   Method A - Command line:")
    print("   huggingface-cli login")
    print("   (Enter your token when prompted)")
    
    print("\n   Method B - Environment variable:")
    print("   set HF_TOKEN=your_token_here")
    print("   (Windows) or export HF_TOKEN=your_token_here (Linux/Mac)")
    
    print("\n   Method C - Python script:")
    print("   from huggingface_hub import login")
    print("   login('your_token_here')")
    
    print("\n5. Test authentication:")
    print("   python -c \"from huggingface_hub import whoami; print(whoami())\"")

def test_dataset_access():
    """Test if we can access the CoVLA dataset"""
    print("\nTesting Dataset Access...")
    print("=" * 30)
    
    try:
        from datasets import load_dataset
        
        # Try to load the mini dataset first
        print("Testing CoVLA-Dataset-Mini...")
        dataset = load_dataset("turing-motors/CoVLA-Dataset-Mini")
        print(f"[OK] Successfully loaded mini dataset!")
        print(f"  Available splits: {list(dataset.keys())}")
        
        # Show sample info
        if 'train' in dataset:
            sample = dataset['train'][0]
            print(f"  Sample keys: {list(sample.keys())}")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to access dataset: {e}")
        return False

def main():
    """Main setup function"""
    print("CoVLA Dataset Setup Assistant")
    print("=" * 50)
    
    # Check current authentication status
    print("Checking authentication status...")
    is_authenticated = check_huggingface_auth()
    
    if not is_authenticated:
        print("\n" + "=" * 50)
        setup_authentication()
        print("\n" + "=" * 50)
        print("After completing the authentication steps above,")
        print("run this script again to test dataset access.")
        return
    
    # Test dataset access
    print("\n" + "=" * 50)
    can_access = test_dataset_access()
    
    if can_access:
        print("\nSetup complete! You can now use the CoVLA dataset.")
        print("\nNext steps:")
        print("1. Run: python test_covla_dataset.py")
        print("2. Run: python train.py")
    else:
        print("\n[X] Setup incomplete. Please follow the authentication steps above.")

if __name__ == '__main__':
    main()

