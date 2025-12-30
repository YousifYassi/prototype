#!/usr/bin/env python3
"""
Check if all required components are set up correctly
"""
import os
import sys

def check_python_packages():
    """Check if required Python packages are installed"""
    print("[*] Checking Python packages...")
    required_packages = [
        'fastapi', 'uvicorn', 'torch', 'torchvision', 'cv2', 
        'yaml', 'sqlalchemy', 'jwt', 'passlib', 'aiosmtplib'
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == 'cv2':
                __import__('cv2')
            elif package == 'yaml':
                __import__('yaml')
            elif package == 'jwt':
                __import__('jwt')
            else:
                __import__(package)
            print(f"  [OK] {package}")
        except ImportError:
            print(f"  [X] {package} - NOT INSTALLED")
            missing.append(package)
    
    if missing:
        print(f"\n[!] Missing packages: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt && pip install -r backend/requirements.txt")
        return False
    return True

def check_model():
    """Check if trained model exists"""
    print("\n[*] Checking AI model...")
    model_path = "checkpoints/best_model.pth"
    if os.path.exists(model_path):
        print(f"  [OK] Model found: {model_path}")
        return True
    else:
        print(f"  [X] Model not found: {model_path}")
        print("  Train the model first with: python train.py")
        return False

def check_config():
    """Check if config file exists"""
    print("\n[*] Checking configuration...")
    if os.path.exists("config.yaml"):
        print("  [OK] config.yaml found")
        return True
    else:
        print("  [X] config.yaml not found")
        return False

def check_backend_env():
    """Check backend environment variables"""
    print("\n[*] Checking backend environment...")
    env_file = "backend/.env"
    
    if not os.path.exists(env_file):
        print(f"  [!] {env_file} not found")
        print("  Copy backend/.env.example to backend/.env and configure it")
        return False
    
    # Check for critical variables
    from dotenv import load_dotenv
    load_dotenv(env_file)
    
    critical = {
        'JWT_SECRET_KEY': os.getenv('JWT_SECRET_KEY'),
        'SMTP_USERNAME or SENDGRID_API_KEY': os.getenv('SMTP_USERNAME') or os.getenv('SENDGRID_API_KEY')
    }
    
    all_ok = True
    for var, value in critical.items():
        if value and value != 'your-' in value:
            print(f"  [OK] {var} configured")
        else:
            print(f"  [!] {var} not configured")
            all_ok = False
    
    return all_ok

def check_frontend():
    """Check if frontend is set up"""
    print("\n[*] Checking frontend...")
    
    if not os.path.exists("frontend/node_modules"):
        print("  [X] Frontend dependencies not installed")
        print("  Run: cd frontend && npm install")
        return False
    
    print("  [OK] Frontend dependencies installed")
    
    if not os.path.exists("frontend/.env"):
        print("  [!] frontend/.env not found")
        print("  Copy frontend/.env.example to frontend/.env and configure it")
        return False
    
    print("  [OK] Frontend environment configured")
    return True

def check_database():
    """Check if database is initialized"""
    print("\n[*] Checking database...")
    
    db_file = "backend/workplace_safety.db"
    if os.path.exists(db_file):
        print(f"  [OK] Database exists: {db_file}")
        return True
    else:
        print(f"  [!] Database not initialized")
        print("  Run: python setup_database.py")
        return False

def main():
    print("=" * 60)
    print("Workplace Safety Monitoring - Setup Check")
    print("=" * 60)
    print()
    
    checks = [
        ("Python Packages", check_python_packages()),
        ("AI Model", check_model()),
        ("Configuration", check_config()),
        ("Backend Environment", check_backend_env()),
        ("Database", check_database()),
        ("Frontend", check_frontend()),
    ]
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    all_passed = True
    for name, passed in checks:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} - {name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("All checks passed! You're ready to start the application.")
        print()
        print("Start backend:  python start_backend.py")
        print("Start frontend: cd frontend && npm run dev")
    else:
        print("[!] Some checks failed. Please fix the issues above.")
        print("\nFor detailed setup instructions, see:")
        print("  WORKPLACE_SAFETY_APP_SETUP.md")
    
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[X] Error during setup check: {e}")
        sys.exit(1)

