#!/usr/bin/env python3
# Jupyter Deployment Script
import os
import subprocess

def setup_jupyter():
    print("📓 Setting up Jupyter deployment...")
    
    # Install Jupyter if not present
    try:
        import jupyter
    except ImportError:
        subprocess.run(["pip", "install", "jupyter"])
    
    # Create Jupyter config
    config_dir = os.path.expanduser("~/.jupyter")
    os.makedirs(config_dir, exist_ok=True)
    
    # Start Jupyter
    subprocess.run(["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser"])

if __name__ == "__main__":
    setup_jupyter()
