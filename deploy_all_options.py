#!/usr/bin/env python3
"""
Comprehensive Deployment Script for All Options
==============================================
Deploy to Nosana, Akash, Docker, or local with one script.
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

class DeploymentManager:
    """Manage deployments to all platforms"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.deploy_dir = self.project_root / "deployment_package"
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Load deployment configuration"""
        config_file = self.project_root / "deployment_config.json"
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        
        # Default configuration
        return {
            "app_name": "telegram-manager-bot",
            "version": "1.0.0",
            "description": "Telegram Manager Bot with AI backends",
            "gpu_requirements": {
                "nosana": {
                    "model": "RTX 3090",
                    "memory": "24GB",
                    "count": 1
                }
            },
            "resources": {
                "cpu": "8 cores",
                "ram": "32GB",
                "storage": "100GB"
            },
            "ports": [8000],
            "environment": {
                "PYTHONPATH": "/app",
                "NODE_ENV": "production"
            }
        }
    
    def show_menu(self):
        """Show deployment options menu"""
        print("🚀 COMPREHENSIVE DEPLOYMENT MANAGER")
        print("=" * 50)
        print()
        print("📋 Available Deployment Options:")
        print("1. 🎯 Nosana GPU (Recommended for production)")
        print("2. 🌐 Akash Network (Alternative decentralized)")
        print("3. 🐳 Docker (Containerized deployment)")
        print("4. 💻 Local Development (Testing)")
        print("5. 📓 Jupyter Notebook (Interactive)")
        print("6. 🔧 Custom Configuration")
        print("7. 📊 Test All Options")
        print("8. 🆘 Help & Documentation")
        print("9. ❌ Exit")
        print()
    
    def check_requirements(self) -> bool:
        """Check deployment requirements"""
        print("🔍 Checking deployment requirements...")
        
        # Check environment variables
        required_vars = [
            "TELEGRAM_BOT_TOKEN",
            "TELEGRAM_API_ID",
            "TELEGRAM_API_HASH",
            "TELEGRAM_PHONE",
            "USER_ID"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing environment variables: {missing_vars}")
            print("💡 Set them in your .env file")
            return False
        
        # Check essential files
        required_files = [
            "telegram_manager_bot_unified.py",
            "requirements.txt",
            ".env"
        ]
        
        missing_files = []
        for file in required_files:
            if not (self.project_root / file).exists():
                missing_files.append(file)
        
        if missing_files:
            print(f"❌ Missing files: {missing_files}")
            return False
        
        print("✅ All requirements met")
        return True
    
    def create_deployment_package(self) -> Path:
        """Create deployment package"""
        print("📦 Creating deployment package...")
        
        # Clean and create deployment directory
        if self.deploy_dir.exists():
            shutil.rmtree(self.deploy_dir)
        self.deploy_dir.mkdir()
        
        # Files to include
        files_to_copy = [
            "telegram_manager_bot.py",
            "telegram_manager_bot_unified.py",
            "telegram_manager_bot_ollama.py",
            "requirements.txt",
            "team_access_manager.py",
            "whitelist_manager.py",
            "google_sheets_integration.py",
            "ollama_client.py",
            "atoma_client.py",
            "elizao_agentic_framework.py",
            "test_suite.py",
            "test_bot_status.py"
        ]
        
        copied_files = []
        for file in files_to_copy:
            src = self.project_root / file
            if src.exists():
                dst = self.deploy_dir / file
                shutil.copy2(src, dst)
                copied_files.append(file)
                print(f"  📄 Copied {file}")
        
        # Create platform-specific files
        self.create_nosana_files()
        self.create_akash_files()
        self.create_docker_files()
        self.create_jupyter_files()
        
        print(f"✅ Deployment package created: {self.deploy_dir}")
        return self.deploy_dir
    
    def create_nosana_files(self):
        """Create Nosana-specific deployment files"""
        # Startup script
        startup_script = """#!/bin/bash
# Nosana Startup Script
echo "🚀 Starting Telegram Manager Bot on Nosana..."

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export PYTHONPATH=/app

# Start the bot
python telegram_manager_bot_unified.py
"""
        
        with open(self.deploy_dir / "start_nosana.sh", 'w') as f:
            f.write(startup_script)
        os.chmod(self.deploy_dir / "start_nosana.sh", 0o755)
        
        # Nosana config
        nosana_config = {
            "name": self.config["app_name"],
            "description": self.config["description"],
            "gpu_requirements": self.config["gpu_requirements"]["nosana"],
            "resources": self.config["resources"],
            "environment": self.config["environment"],
            "ports": self.config["ports"],
            "startup_command": "./start_nosana.sh"
        }
        
        with open(self.deploy_dir / "nosana_config.json", 'w') as f:
            json.dump(nosana_config, f, indent=2)
    
    def create_akash_files(self):
        """Create Akash-specific deployment files"""
        # Akash deployment manifest
        akash_manifest = f"""---
version: "2.0"
services:
  - name: {self.config["app_name"]}
    image: python:3.9-slim
    args: ["-c", "pip install -r requirements.txt && python telegram_manager_bot_unified.py"]
    env:
      - PYTHONPATH=/app
    resources:
      cpu:
        units: 4.0
      memory:
        size: 8Gi
      storage:
        - size: 50Gi
    expose:
      - port: 8000
        as: 80
        to:
          - global: true
profiles:
  compute:
    {self.config["app_name"]}:
      resources:
        cpu:
          units: 4.0
        memory:
          size: 8Gi
        storage:
          - size: 50Gi
  placement:
    {self.config["app_name"]}:
      pricing:
        {self.config["app_name"]}:
          denom: uakt
          amount: 1000
deployment:
  {self.config["app_name"]}:
    {self.config["app_name"]}:
      profile: {self.config["app_name"]}
      count: 1
"""
        
        with open(self.deploy_dir / "akash_deployment.yml", 'w') as f:
            f.write(akash_manifest)
    
    def create_docker_files(self):
        """Create Docker-specific deployment files"""
        # Dockerfile
        dockerfile = """FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Make startup script executable
RUN chmod +x start_nosana.sh

# Expose port
EXPOSE 8000

# Start the application
CMD ["./start_nosana.sh"]
"""
        
        with open(self.deploy_dir / "Dockerfile", 'w') as f:
            f.write(dockerfile)
        
        # docker-compose.yml
        docker_compose = f"""version: '3.8'

services:
  {self.config["app_name"]}:
    build: .
    container_name: {self.config["app_name"]}
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app
    volumes:
      - ./logs:/app/logs
    env_file:
      - .env
"""
        
        with open(self.deploy_dir / "docker-compose.yml", 'w') as f:
            f.write(docker_compose)
    
    def create_jupyter_files(self):
        """Create Jupyter-specific files"""
        # Jupyter deployment script
        jupyter_script = """#!/usr/bin/env python3
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
"""
        
        with open(self.deploy_dir / "jupyter_setup.py", 'w') as f:
            f.write(jupyter_script)
    
    def deploy_to_nosana(self):
        """Deploy to Nosana"""
        print("🚀 Deploying to Nosana...")
        
        nosana_key = os.getenv('NOSANA_API_KEY')
        if not nosana_key:
            print("❌ NOSANA_API_KEY not found")
            print("💡 Get it from: https://nosana.com/dashboard")
            return False
        
        print("📋 Nosana Deployment Steps:")
        print("1. Go to https://nosana.com")
        print("2. Click 'Deploy Now'")
        print("3. Upload files from deployment_package/")
        print("4. Select GPU: RTX 3090 (24GB)")
        print("5. Set environment variables")
        print("6. Deploy!")
        
        print(f"\n📁 Files ready in: {self.deploy_dir}")
        return True
    
    def deploy_to_akash(self):
        """Deploy to Akash"""
        print("🌐 Deploying to Akash...")
        
        # Check if Akash CLI is installed
        try:
            result = subprocess.run(["akash", "version"], capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Akash CLI not found")
                print("💡 Install from: https://docs.akash.network/guides/install")
                return False
        except FileNotFoundError:
            print("❌ Akash CLI not installed")
            print("💡 Install from: https://docs.akash.network/guides/install")
            return False
        
        print("📋 Akash Deployment Steps:")
        print("1. Ensure Akash CLI is installed")
        print("2. Create deployment:")
        print(f"   akash tx deployment create {self.deploy_dir}/akash_deployment.yml")
        print("3. Follow Akash CLI prompts")
        
        return True
    
    def deploy_with_docker(self):
        """Deploy with Docker"""
        print("🐳 Deploying with Docker...")
        
        # Check if Docker is available
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Docker not available")
                return False
        except FileNotFoundError:
            print("❌ Docker not installed")
            return False
        
        print("📋 Docker Deployment Steps:")
        print("1. Build image:")
        print(f"   cd {self.deploy_dir}")
        print("   docker build -t telegram-bot .")
        print("2. Run container:")
        print("   docker run -d --name telegram-bot telegram-bot")
        print("3. Or use docker-compose:")
        print("   docker-compose up -d")
        
        return True
    
    def deploy_locally(self):
        """Deploy locally"""
        print("💻 Setting up local deployment...")
        
        print("📋 Local Deployment Steps:")
        print("1. Install Ollama (if using local AI):")
        print("   curl -fsSL https://ollama.ai/install.sh | sh")
        print("2. Pull AI model:")
        print("   ollama pull llama3.2:3b")
        print("3. Run bot:")
        print("   python telegram_manager_bot_unified.py")
        
        return True
    
    def deploy_jupyter(self):
        """Deploy with Jupyter"""
        print("📓 Setting up Jupyter deployment...")
        
        print("📋 Jupyter Deployment Steps:")
        print("1. Start Jupyter:")
        print("   jupyter notebook")
        print("2. Open nosana_jupyter_setup.ipynb")
        print("3. Follow notebook instructions")
        
        return True
    
    def test_all_options(self):
        """Test all deployment options"""
        print("🧪 Testing all deployment options...")
        
        tests = [
            ("Environment Variables", self.check_requirements),
            ("Nosana API Key", lambda: bool(os.getenv('NOSANA_API_KEY'))),
            ("Docker Available", lambda: subprocess.run(["docker", "--version"], capture_output=True).returncode == 0),
            ("Akash CLI", lambda: subprocess.run(["akash", "version"], capture_output=True).returncode == 0),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                status = "✅ PASS" if result else "❌ FAIL"
                results.append((test_name, status))
                print(f"{status} {test_name}")
            except Exception as e:
                results.append((test_name, f"❌ ERROR: {e}"))
                print(f"❌ ERROR {test_name}: {e}")
        
        print(f"\n📊 Test Results: {len([r for r in results if 'PASS' in r[1]])}/{len(results)} passed")
        return results
    
    def show_help(self):
        """Show help and documentation"""
        help_text = """
📚 DEPLOYMENT HELP & DOCUMENTATION
==================================

🎯 RECOMMENDED DEPLOYMENT OPTIONS:

1. 🚀 NOSANA (Production Teams)
   - Best for: AI workloads, 24/7 operation
   - Cost: $350-400/month (RTX 3090)
   - Setup: Web interface or CLI
   - GPU: RTX 3090/4090 recommended

2. 🌐 AKASH (Alternative Decentralized)
   - Best for: Cost-conscious decentralized hosting
   - Cost: Variable (typically cheaper)
   - Setup: CLI deployment
   - Resources: CPU-based

3. 🐳 DOCKER (Consistent Environments)
   - Best for: Development, testing, easy scaling
   - Cost: Free (your infrastructure)
   - Setup: Container deployment
   - Resources: Your hardware

4. 💻 LOCAL (Development)
   - Best for: Testing, small teams
   - Cost: Free
   - Setup: Direct execution
   - Resources: Your computer

📋 PREREQUISITES:

Required Environment Variables:
- TELEGRAM_BOT_TOKEN
- TELEGRAM_API_ID
- TELEGRAM_API_HASH
- TELEGRAM_PHONE
- USER_ID

Optional (for specific deployments):
- NOSANA_API_KEY (for Nosana)
- ATOMA_API_KEY (for Atoma AI)
- GOOGLE_SERVICE_ACCOUNT_FILE (for Google Sheets)

🔧 TROUBLESHOOTING:

Common Issues:
1. Missing environment variables → Check .env file
2. API keys not found → Get from respective dashboards
3. Docker not available → Install Docker Desktop
4. Akash CLI missing → Install from Akash docs

📞 SUPPORT:
- Documentation: README_UNIFIED.md
- Issues: GitHub repository
- Community: Discord/Telegram channels
"""
        print(help_text)
    
    def run(self):
        """Main deployment manager loop"""
        while True:
            self.show_menu()
            
            try:
                choice = input("Select option (1-9): ").strip()
                
                if choice == "1":
                    if self.check_requirements():
                        self.create_deployment_package()
                        self.deploy_to_nosana()
                    else:
                        print("❌ Please fix requirements first")
                
                elif choice == "2":
                    if self.check_requirements():
                        self.create_deployment_package()
                        self.deploy_to_akash()
                    else:
                        print("❌ Please fix requirements first")
                
                elif choice == "3":
                    if self.check_requirements():
                        self.create_deployment_package()
                        self.deploy_with_docker()
                    else:
                        print("❌ Please fix requirements first")
                
                elif choice == "4":
                    self.deploy_locally()
                
                elif choice == "5":
                    self.deploy_jupyter()
                
                elif choice == "6":
                    print("🔧 Custom configuration options:")
                    print("1. Edit deployment_config.json")
                    print("2. Modify environment variables")
                    print("3. Customize startup scripts")
                    print("4. Add custom dependencies")
                
                elif choice == "7":
                    self.test_all_options()
                
                elif choice == "8":
                    self.show_help()
                
                elif choice == "9":
                    print("👋 Goodbye!")
                    break
                
                else:
                    print("❌ Invalid option")
                
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                input("Press Enter to continue...")

def main():
    """Main function"""
    print("🚀 COMPREHENSIVE DEPLOYMENT MANAGER")
    print("=" * 50)
    
    manager = DeploymentManager()
    manager.run()

if __name__ == "__main__":
    main() 