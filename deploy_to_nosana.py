#!/usr/bin/env python3
"""
Nosana Deployment Script with SDK Integration
=============================================
Deploy your Telegram bot to Nosana compute using the official SDK.
"""

import os
import json
import shutil
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import our Nosana client
from nosana_client import NosanaClient, NosanaDeploymentManager, NosanaDeploymentConfig

class NosanaDeployer:
    """Enhanced Nosana deployment with SDK integration"""
    
    def __init__(self):
        self.nosana_api_key = os.getenv('NOSANA_API_KEY')
        self.deployment_manager = None
        self.client = None
        
        if self.nosana_api_key:
            try:
                self.client = NosanaClient(self.nosana_api_key)
                self.deployment_manager = NosanaDeploymentManager(self.nosana_api_key)
                print("✅ Nosana SDK initialized")
            except Exception as e:
                print(f"❌ Failed to initialize Nosana SDK: {e}")
    
    def check_requirements(self) -> bool:
        """Check if we have what we need"""
        print("🔍 Checking requirements...")
        
        if not self.nosana_api_key:
            print("❌ NOSANA_API_KEY not found in environment")
            print("💡 Set it with: export NOSANA_API_KEY=your_key_here")
            print("💡 Get it from: https://nosana.com/dashboard")
            return False
        
        if not self.client:
            print("❌ Nosana client not initialized")
            return False
        
        # Test connection
        print("🔗 Testing Nosana API connection...")
        if not self.client.test_connection():
            print("❌ Failed to connect to Nosana API")
            print("💡 Check your API key and internet connection")
            return False
        
        print("✅ Nosana API connection successful")
        
        # Check if we have the bot files
        required_files = [
            "telegram_manager_bot_unified.py",
            "requirements.txt",
            ".env"
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files:
            print(f"❌ Missing files: {', '.join(missing_files)}")
            return False
        
        print("✅ All requirements met")
        return True
    
    def create_deployment_package(self) -> str:
        """Create deployment package"""
        print("📦 Creating deployment package...")
        
        # Create deployment directory
        deploy_dir = f"nosana_deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if os.path.exists(deploy_dir):
            shutil.rmtree(deploy_dir)
        os.makedirs(deploy_dir)
        
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
            if os.path.exists(file):
                shutil.copy2(file, deploy_dir)
                copied_files.append(file)
                print(f"  📄 Copied {file}")
        
        # Create startup script
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
        
        with open(f"{deploy_dir}/start.sh", 'w') as f:
            f.write(startup_script)
        os.chmod(f"{deploy_dir}/start.sh", 0o755)
        print("  📄 Created start.sh")
        
        # Create Dockerfile
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
RUN chmod +x start.sh

# Expose port
EXPOSE 8000

# Start the application
CMD ["./start.sh"]
"""
        
        with open(f"{deploy_dir}/Dockerfile", 'w') as f:
            f.write(dockerfile)
        print("  📄 Created Dockerfile")
        
        # Create deployment config
        config = {
            "name": "telegram-manager-bot",
            "description": "Telegram Manager Bot with AI backends",
            "gpu_requirements": {
                "model": "RTX 3090",
                "memory": "24GB",
                "count": 1
            },
            "resources": {
                "cpu": "8 cores",
                "ram": "32GB",
                "storage": "100GB"
            },
            "environment": {
                "PYTHONPATH": "/app",
                "NODE_ENV": "production"
            },
            "ports": [8000],
            "startup_command": "./start.sh"
        }
        
        with open(f"{deploy_dir}/nosana_config.json", 'w') as f:
            json.dump(config, f, indent=2)
        print("  📄 Created nosana_config.json")
        
        print(f"✅ Deployment package created: {deploy_dir}")
        return deploy_dir
    
    def get_environment_variables(self) -> Dict[str, str]:
        """Get environment variables for deployment"""
        env_vars = {}
        
        # Required Telegram variables
        required_vars = [
            "TELEGRAM_BOT_TOKEN",
            "TELEGRAM_API_ID",
            "TELEGRAM_API_HASH",
            "TELEGRAM_PHONE",
            "USER_ID"
        ]
        
        for var in required_vars:
            value = os.getenv(var)
            if value:
                env_vars[var] = value
            else:
                print(f"⚠️  Warning: {var} not set")
        
        # Optional variables
        optional_vars = [
            "ATOMA_API_KEY",
            "GOOGLE_SERVICE_ACCOUNT_FILE",
            "GOOGLE_SPREADSHEET_ID",
            "OLLAMA_BASE_URL",
            "AI_BACKEND"
        ]
        
        for var in optional_vars:
            value = os.getenv(var)
            if value:
                env_vars[var] = value
        
        return env_vars
    
    def deploy_to_nosana(self, deploy_dir: str) -> Optional[str]:
        """Deploy to Nosana using SDK"""
        print("🚀 Deploying to Nosana using SDK...")
        
        try:
            # Get environment variables
            env_vars = self.get_environment_variables()
            
            # Deploy using the SDK
            deployment_id = self.deployment_manager.deploy_telegram_bot(
                project_name="telegram-manager-bot",
                environment_vars=env_vars
            )
            
            if deployment_id:
                print(f"✅ Deployment initiated: {deployment_id}")
                
                # Wait for deployment to be ready
                print("⏳ Waiting for deployment to be ready...")
                status = self.deployment_manager.monitor_deployment(deployment_id)
                
                if status and status.status == "running":
                    print(f"🎉 Deployment ready!")
                    print(f"📊 Status: {status.status}")
                    print(f"💰 Cost per hour: ${status.cost_per_hour}")
                    if status.url:
                        print(f"🌐 URL: {status.url}")
                    
                    # Save deployment info
                    deployment_info = {
                        "deployment_id": deployment_id,
                        "status": status.status,
                        "url": status.url,
                        "cost_per_hour": status.cost_per_hour,
                        "created_at": datetime.now().isoformat(),
                        "deploy_dir": deploy_dir
                    }
                    
                    with open("nosana_deployment_info.json", 'w') as f:
                        json.dump(deployment_info, f, indent=2)
                    
                    print("📄 Deployment info saved to nosana_deployment_info.json")
                    return deployment_id
                else:
                    print(f"❌ Deployment failed or timed out")
                    if status:
                        print(f"Error: {status.error_message}")
                    return None
            else:
                print("❌ Failed to create deployment")
                return None
                
        except Exception as e:
            print(f"❌ Deployment error: {e}")
            return None
    
    async def deploy_to_nosana_async(self, deploy_dir: str) -> Optional[str]:
        """Async deployment to Nosana"""
        print("🚀 Deploying to Nosana using SDK (async)...")
        
        try:
            # Get environment variables
            env_vars = self.get_environment_variables()
            
            # Deploy using the SDK
            deployment_id = await self.deployment_manager.deploy_telegram_bot_async(
                project_name="telegram-manager-bot",
                environment_vars=env_vars
            )
            
            if deployment_id:
                print(f"✅ Deployment initiated: {deployment_id}")
                
                # Wait for deployment to be ready
                print("⏳ Waiting for deployment to be ready...")
                status = self.deployment_manager.monitor_deployment(deployment_id)
                
                if status and status.status == "running":
                    print(f"🎉 Deployment ready!")
                    print(f"📊 Status: {status.status}")
                    print(f"💰 Cost per hour: ${status.cost_per_hour}")
                    if status.url:
                        print(f"🌐 URL: {status.url}")
                    
                    return deployment_id
                else:
                    print(f"❌ Deployment failed or timed out")
                    return None
            else:
                print("❌ Failed to create deployment")
                return None
                
        except Exception as e:
            print(f"❌ Deployment error: {e}")
            return None
    
    def list_deployments(self):
        """List all deployments"""
        print("📋 Listing deployments...")
        
        try:
            deployments = self.client.get_deployments()
            
            if deployments:
                print(f"Found {len(deployments)} deployments:")
                for deployment in deployments:
                    print(f"  - {deployment.get('name', 'Unknown')} ({deployment.get('status', 'Unknown')})")
                    print(f"    ID: {deployment.get('id', 'Unknown')}")
                    if deployment.get('url'):
                        print(f"    URL: {deployment.get('url')}")
                    print()
            else:
                print("No deployments found")
                
        except Exception as e:
            print(f"❌ Error listing deployments: {e}")
    
    def get_deployment_info(self, deployment_id: str):
        """Get detailed deployment information"""
        print(f"📊 Getting deployment info for {deployment_id}...")
        
        try:
            status = self.client.get_deployment_status(deployment_id)
            
            if status:
                print(f"📊 Deployment Status:")
                print(f"  - ID: {status.deployment_id}")
                print(f"  - Status: {status.status}")
                print(f"  - Created: {status.created_at}")
                print(f"  - Updated: {status.updated_at}")
                print(f"  - Cost per hour: ${status.cost_per_hour}")
                if status.url:
                    print(f"  - URL: {status.url}")
                if status.error_message:
                    print(f"  - Error: {status.error_message}")
            else:
                print("❌ Deployment not found")
                
        except Exception as e:
            print(f"❌ Error getting deployment info: {e}")
    
    def stop_deployment(self, deployment_id: str):
        """Stop a deployment"""
        print(f"🛑 Stopping deployment {deployment_id}...")
        
        try:
            success = self.client.stop_deployment(deployment_id)
            if success:
                print("✅ Deployment stopped")
            else:
                print("❌ Failed to stop deployment")
        except Exception as e:
            print(f"❌ Error stopping deployment: {e}")
    
    def delete_deployment(self, deployment_id: str):
        """Delete a deployment"""
        print(f"🗑️  Deleting deployment {deployment_id}...")
        
        try:
            success = self.client.delete_deployment(deployment_id)
            if success:
                print("✅ Deployment deleted")
            else:
                print("❌ Failed to delete deployment")
        except Exception as e:
            print(f"❌ Error deleting deployment: {e}")
    
    def get_logs(self, deployment_id: str):
        """Get deployment logs"""
        print(f"📋 Getting logs for deployment {deployment_id}...")
        
        try:
            logs = self.client.get_logs(deployment_id)
            if logs:
                print("📋 Recent logs:")
                print(logs)
            else:
                print("No logs available")
        except Exception as e:
            print(f"❌ Error getting logs: {e}")
    
    def get_billing_info(self):
        """Get billing information"""
        print("💰 Getting billing information...")
        
        try:
            billing = self.client.get_billing_info()
            if billing:
                print(f"💰 Billing Info:")
                print(f"  - Balance: ${billing.get('balance', 'Unknown')}")
                print(f"  - Usage: ${billing.get('usage', 'Unknown')}")
                print(f"  - Currency: {billing.get('currency', 'USD')}")
            else:
                print("No billing information available")
        except Exception as e:
            print(f"❌ Error getting billing info: {e}")

def main():
    """Main deployment function"""
    print("🚀 NOSANA DEPLOYMENT SCRIPT (SDK)")
    print("=" * 50)
    
    deployer = NosanaDeployer()
    
    while True:
        print("\n📋 Available Options:")
        print("1. 🚀 Deploy Telegram Bot")
        print("2. 📋 List Deployments")
        print("3. 📊 Get Deployment Info")
        print("4. 🛑 Stop Deployment")
        print("5. 🗑️  Delete Deployment")
        print("6. 📋 Get Logs")
        print("7. 💰 Get Billing Info")
        print("8. 📦 Create Package Only")
        print("9. ❌ Exit")
        
        choice = input("\nSelect option (1-9): ").strip()
        
        if choice == "1":
            if deployer.check_requirements():
                deploy_dir = deployer.create_deployment_package()
                
                # Ask for deployment method
                method = input("Deploy method (sync/async): ").strip().lower()
                
                if method == "async":
                    deployment_id = asyncio.run(deployer.deploy_to_nosana_async(deploy_dir))
                else:
                    deployment_id = deployer.deploy_to_nosana(deploy_dir)
                
                if deployment_id:
                    print(f"🎉 Deployment successful! ID: {deployment_id}")
                else:
                    print("❌ Deployment failed")
            else:
                print("❌ Requirements not met")
        
        elif choice == "2":
            deployer.list_deployments()
        
        elif choice == "3":
            deployment_id = input("Enter deployment ID: ").strip()
            deployer.get_deployment_info(deployment_id)
        
        elif choice == "4":
            deployment_id = input("Enter deployment ID: ").strip()
            deployer.stop_deployment(deployment_id)
        
        elif choice == "5":
            deployment_id = input("Enter deployment ID: ").strip()
            confirm = input("Are you sure? (yes/no): ").strip().lower()
            if confirm == "yes":
                deployer.delete_deployment(deployment_id)
        
        elif choice == "6":
            deployment_id = input("Enter deployment ID: ").strip()
            deployer.get_logs(deployment_id)
        
        elif choice == "7":
            deployer.get_billing_info()
        
        elif choice == "8":
            deploy_dir = deployer.create_deployment_package()
            print(f"📦 Package created: {deploy_dir}")
        
        elif choice == "9":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main() 