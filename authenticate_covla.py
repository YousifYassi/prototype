#!/usr/bin/env python3
"""
Simple CoVLA Authentication Helper
"""
import os
import sys

def authenticate_with_token():
    """Authenticate using a token"""
    print("CoVLA Dataset Authentication")
    print("=" * 40)
    
    print("\nTo access the CoVLA dataset, you need to:")
    print("1. Visit: https://huggingface.co/datasets/turing-motors/CoVLA-Dataset")
    print("2. Click 'Request access' and accept the license terms")
    print("3. Get your token from: https://huggingface.co/settings/tokens")
    print("4. Create a token with 'Read' permissions")
    
    print("\nEnter your Hugging Face token:")
    token = input("Token: ").strip()
    
    if not token:
        print("No token provided. Exiting.")
        return False
    
    try:
        # Set environment variable
        os.environ['HF_TOKEN'] = token
        
        # Test authentication
        from huggingface_hub import whoami
        user_info = whoami()
        print(f"\n✓ Successfully authenticated as: {user_info['name']}")
        
        # Save token for future use
        print("\nSaving token for future use...")
        try:
            from huggingface_hub import login
            login(token)
            print("✓ Token saved successfully!")
        except Exception as e:
            print(f"⚠ Could not save token: {e}")
            print("You may need to authenticate again next time.")
        
        return True
        
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        print("\nPlease check:")
        print("1. Your token is correct")
        print("2. You have accepted the license terms")
        print("3. Your token has 'Read' permissions")
        return False

def test_dataset_access():
    """Test if we can access the CoVLA dataset"""
    print("\nTesting dataset access...")
    print("=" * 30)
    
    try:
        from datasets import load_dataset
        
        print("Loading CoVLA-Dataset-Mini (for testing)...")
        dataset = load_dataset("turing-motors/CoVLA-Dataset-Mini")
        
        print(f"✓ Successfully loaded dataset!")
        print(f"  Available splits: {list(dataset.keys())}")
        
        if 'train' in dataset and len(dataset['train']) > 0:
            sample = dataset['train'][0]
            print(f"  Sample keys: {list(sample.keys())}")
            print(f"  Number of samples: {len(dataset['train'])}")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to access dataset: {e}")
        return False

def main():
    """Main authentication flow"""
    print("CoVLA Dataset Authentication Helper")
    print("=" * 50)
    
    # Check if already authenticated
    try:
        from huggingface_hub import whoami
        user_info = whoami()
        print(f"✓ Already authenticated as: {user_info['name']}")
        
        # Test dataset access
        if test_dataset_access():
            print("\n🎉 Everything is set up correctly!")
            print("You can now run: python train.py")
            return
        
    except Exception:
        print("Not authenticated. Starting authentication process...")
    
    # Authenticate
    if authenticate_with_token():
        # Test dataset access
        if test_dataset_access():
            print("\n🎉 Setup complete! You can now use the CoVLA dataset.")
            print("\nNext steps:")
            print("1. Run: python test_covla_dataset.py")
            print("2. Run: python train.py")
        else:
            print("\n❌ Authentication succeeded but dataset access failed.")
            print("Please check the license terms acceptance.")
    else:
        print("\n❌ Authentication failed. Please try again.")

if __name__ == '__main__':
    main()

