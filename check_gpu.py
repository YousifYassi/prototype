"""
Quick script to check GPU availability and provide installation instructions
"""
import torch
import sys

print("=" * 60)
print("GPU Availability Check")
print("=" * 60)

print(f"\nPyTorch Version: {torch.__version__}")
print(f"CUDA Available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"CUDA Version: {torch.version.cuda}")
    print(f"cuDNN Version: {torch.backends.cudnn.version()}")
    print(f"\nGPU Device(s):")
    for i in range(torch.cuda.device_count()):
        props = torch.cuda.get_device_properties(i)
        print(f"  [{i}] {torch.cuda.get_device_name(i)}")
        print(f"      Memory: {props.total_memory / 1024**3:.1f} GB")
        print(f"      Compute Capability: {props.major}.{props.minor}")
    
    print("\n[SUCCESS] GPU is available for training!")
    print("Your config.yaml is already set to use CUDA.")
else:
    print("\n[INFO] CUDA is not available.")
    print("\nYour System Info:")
    try:
        import subprocess
        result = subprocess.run(['wmic', 'path', 'win32_VideoController', 'get', 'name'], 
                              capture_output=True, text=True, timeout=5)
        if "NVIDIA" in result.stdout:
            print("  - NVIDIA GPU detected in system")
            print("\n[RECOMMENDATION] Install PyTorch with CUDA support:")
            print("\n  Step 1: Uninstall CPU-only PyTorch")
            print("    pip uninstall torch torchvision torchaudio")
            print("\n  Step 2: Install PyTorch with CUDA 12.1")
            print("    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
            print("\n  Alternative: Install with CUDA 11.8")
            print("    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
            print("\n  Step 3: Run this script again to verify")
            print("    python check_gpu.py")
            print("\n  Step 4: Update config.yaml device setting to 'cuda'")
            print("\nTraining Speed Improvement: 10-30x faster with GPU!")
        else:
            print("  - No NVIDIA GPU detected")
            print("  - CPU training will be used")
            print("\n[INFO] Your config.yaml should use device: 'cpu'")
    except:
        print("  - Could not detect GPU information")

print("\n" + "=" * 60)

# Test a simple tensor operation
print("\nQuick Performance Test:")
try:
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Creating tensor on: {device}")
    
    import time
    x = torch.randn(1000, 1000, device=device)
    
    start = time.time()
    for _ in range(100):
        y = torch.matmul(x, x)
    elapsed = time.time() - start
    
    print(f"100 matrix multiplications (1000x1000): {elapsed:.3f}s")
    if torch.cuda.is_available():
        print(f"GPU Memory Allocated: {torch.cuda.memory_allocated() / 1024**2:.1f} MB")
        print(f"GPU Memory Cached: {torch.cuda.memory_reserved() / 1024**2:.1f} MB")
except Exception as e:
    print(f"Performance test failed: {e}")

print("=" * 60)

