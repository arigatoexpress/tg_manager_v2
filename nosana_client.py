#!/usr/bin/env python3
"""
Nosana SDK Client Implementation
================================
Complete integration with Nosana API for deployment and management.
"""

import os
import json
import time
import asyncio
import aiohttp
import requests
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class NosanaDeploymentConfig:
    """Configuration for Nosana deployment"""
    name: str
    description: str
    docker_image: str = "python:3.9-slim"
    gpu_model: str = "RTX 3090"
    gpu_memory: str = "24GB"
    cpu_cores: int = 8
    ram_gb: int = 32
    storage_gb: int = 100
    ports: List[int] = None
    environment_vars: Dict[str, str] = None
    startup_command: str = "./start.sh"
    restart_policy: str = "always"
    
    def __post_init__(self):
        if self.ports is None:
            self.ports = [8000]
        if self.environment_vars is None:
            self.environment_vars = {}

@dataclass
class NosanaDeploymentStatus:
    """Deployment status information"""
    deployment_id: str
    status: str  # creating, running, stopped, failed, deleted
    created_at: datetime
    updated_at: datetime
    url: Optional[str] = None
    cost_per_hour: Optional[float] = None
    logs: Optional[str] = None
    error_message: Optional[str] = None

class NosanaClient:
    """Complete Nosana SDK client"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.nosana.com"):
        self.api_key = api_key or os.getenv('NOSANA_API_KEY')
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
        if not self.api_key:
            raise ValueError("NOSANA_API_KEY is required")
        
        # Set up headers
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "TelegramManagerBot/1.0"
        })
        
        # API endpoints
        self.endpoints = {
            "deployments": f"{self.base_url}/v1/deployments",
            "projects": f"{self.base_url}/v1/projects",
            "gpus": f"{self.base_url}/v1/gpus",
            "billing": f"{self.base_url}/v1/billing",
            "logs": f"{self.base_url}/v1/logs"
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                     params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to Nosana API"""
        url = endpoint
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Nosana API request failed: {e}")
            raise Exception(f"Nosana API error: {e}")
    
    async def _make_async_request(self, method: str, endpoint: str, data: Optional[Dict] = None,
                                params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make async HTTP request to Nosana API"""
        url = endpoint
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=self.session.headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            logger.error(f"Nosana API async request failed: {e}")
            raise Exception(f"Nosana API async error: {e}")
    
    def test_connection(self) -> bool:
        """Test connection to Nosana API"""
        try:
            response = self._make_request("GET", f"{self.base_url}/v1/health")
            return response.get("status") == "healthy"
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_available_gpus(self) -> List[Dict[str, Any]]:
        """Get available GPU configurations"""
        try:
            response = self._make_request("GET", self.endpoints["gpus"])
            return response.get("gpus", [])
        except Exception as e:
            logger.error(f"Failed to get GPU list: {e}")
            return []
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """Get user's projects"""
        try:
            response = self._make_request("GET", self.endpoints["projects"])
            return response.get("projects", [])
        except Exception as e:
            logger.error(f"Failed to get projects: {e}")
            return []
    
    def create_project(self, name: str, description: str = "") -> Optional[str]:
        """Create a new project"""
        try:
            data = {
                "name": name,
                "description": description
            }
            response = self._make_request("POST", self.endpoints["projects"], data=data)
            return response.get("project_id")
        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            return None
    
    def deploy_application(self, config: NosanaDeploymentConfig, 
                          project_id: Optional[str] = None) -> Optional[str]:
        """Deploy application to Nosana"""
        try:
            # Create project if not provided
            if not project_id:
                project_id = self.create_project(f"{config.name}-project", config.description)
                if not project_id:
                    raise Exception("Failed to create project")
            
            # Prepare deployment payload
            deployment_data = {
                "project_id": project_id,
                "name": config.name,
                "description": config.description,
                "docker_image": config.docker_image,
                "resources": {
                    "gpu": {
                        "model": config.gpu_model,
                        "memory": config.gpu_memory,
                        "count": 1
                    },
                    "cpu": {
                        "cores": config.cpu_cores
                    },
                    "memory": f"{config.ram_gb}Gi",
                    "storage": f"{config.storage_gb}Gi"
                },
                "ports": config.ports,
                "environment": config.environment_vars,
                "startup_command": config.startup_command,
                "restart_policy": config.restart_policy
            }
            
            response = self._make_request("POST", self.endpoints["deployments"], data=deployment_data)
            deployment_id = response.get("deployment_id")
            
            if deployment_id:
                logger.info(f"Deployment created: {deployment_id}")
                return deployment_id
            else:
                raise Exception("No deployment ID returned")
                
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            return None
    
    async def deploy_application_async(self, config: NosanaDeploymentConfig,
                                     project_id: Optional[str] = None) -> Optional[str]:
        """Async version of deploy_application"""
        try:
            # Create project if not provided
            if not project_id:
                project_id = await self.create_project_async(f"{config.name}-project", config.description)
                if not project_id:
                    raise Exception("Failed to create project")
            
            # Prepare deployment payload
            deployment_data = {
                "project_id": project_id,
                "name": config.name,
                "description": config.description,
                "docker_image": config.docker_image,
                "resources": {
                    "gpu": {
                        "model": config.gpu_model,
                        "memory": config.gpu_memory,
                        "count": 1
                    },
                    "cpu": {
                        "cores": config.cpu_cores
                    },
                    "memory": f"{config.ram_gb}Gi",
                    "storage": f"{config.storage_gb}Gi"
                },
                "ports": config.ports,
                "environment": config.environment_vars,
                "startup_command": config.startup_command,
                "restart_policy": config.restart_policy
            }
            
            response = await self._make_async_request("POST", self.endpoints["deployments"], data=deployment_data)
            deployment_id = response.get("deployment_id")
            
            if deployment_id:
                logger.info(f"Deployment created: {deployment_id}")
                return deployment_id
            else:
                raise Exception("No deployment ID returned")
                
        except Exception as e:
            logger.error(f"Async deployment failed: {e}")
            return None
    
    async def create_project_async(self, name: str, description: str = "") -> Optional[str]:
        """Async version of create_project"""
        try:
            data = {
                "name": name,
                "description": description
            }
            response = await self._make_async_request("POST", self.endpoints["projects"], data=data)
            return response.get("project_id")
        except Exception as e:
            logger.error(f"Failed to create project async: {e}")
            return None
    
    def get_deployment_status(self, deployment_id: str) -> Optional[NosanaDeploymentStatus]:
        """Get deployment status"""
        try:
            response = self._make_request("GET", f"{self.endpoints['deployments']}/{deployment_id}")
            
            return NosanaDeploymentStatus(
                deployment_id=deployment_id,
                status=response.get("status", "unknown"),
                created_at=datetime.fromisoformat(response.get("created_at", datetime.now().isoformat())),
                updated_at=datetime.fromisoformat(response.get("updated_at", datetime.now().isoformat())),
                url=response.get("url"),
                cost_per_hour=response.get("cost_per_hour"),
                logs=response.get("logs"),
                error_message=response.get("error_message")
            )
        except Exception as e:
            logger.error(f"Failed to get deployment status: {e}")
            return None
    
    def get_deployments(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all deployments"""
        try:
            params = {}
            if project_id:
                params["project_id"] = project_id
            
            response = self._make_request("GET", self.endpoints["deployments"], params=params)
            return response.get("deployments", [])
        except Exception as e:
            logger.error(f"Failed to get deployments: {e}")
            return []
    
    def stop_deployment(self, deployment_id: str) -> bool:
        """Stop a deployment"""
        try:
            response = self._make_request("POST", f"{self.endpoints['deployments']}/{deployment_id}/stop")
            return response.get("success", False)
        except Exception as e:
            logger.error(f"Failed to stop deployment: {e}")
            return False
    
    def start_deployment(self, deployment_id: str) -> bool:
        """Start a deployment"""
        try:
            response = self._make_request("POST", f"{self.endpoints['deployments']}/{deployment_id}/start")
            return response.get("success", False)
        except Exception as e:
            logger.error(f"Failed to start deployment: {e}")
            return False
    
    def delete_deployment(self, deployment_id: str) -> bool:
        """Delete a deployment"""
        try:
            response = self._make_request("DELETE", f"{self.endpoints['deployments']}/{deployment_id}")
            return response.get("success", False)
        except Exception as e:
            logger.error(f"Failed to delete deployment: {e}")
            return False
    
    def get_logs(self, deployment_id: str, lines: int = 100) -> Optional[str]:
        """Get deployment logs"""
        try:
            params = {"lines": lines}
            response = self._make_request("GET", f"{self.endpoints['logs']}/{deployment_id}", params=params)
            return response.get("logs")
        except Exception as e:
            logger.error(f"Failed to get logs: {e}")
            return None
    
    def get_billing_info(self) -> Dict[str, Any]:
        """Get billing information"""
        try:
            response = self._make_request("GET", self.endpoints["billing"])
            return response
        except Exception as e:
            logger.error(f"Failed to get billing info: {e}")
            return {}
    
    def wait_for_deployment(self, deployment_id: str, timeout: int = 300, 
                          check_interval: int = 10) -> Optional[NosanaDeploymentStatus]:
        """Wait for deployment to be ready"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_deployment_status(deployment_id)
            
            if not status:
                logger.error("Failed to get deployment status")
                return None
            
            logger.info(f"Deployment {deployment_id} status: {status.status}")
            
            if status.status == "running":
                logger.info(f"Deployment {deployment_id} is ready!")
                return status
            elif status.status == "failed":
                logger.error(f"Deployment {deployment_id} failed: {status.error_message}")
                return status
            elif status.status == "stopped":
                logger.warning(f"Deployment {deployment_id} stopped")
                return status
            
            time.sleep(check_interval)
        
        logger.error(f"Deployment {deployment_id} timed out after {timeout} seconds")
        return None
    
    def upload_files(self, deployment_id: str, files: Dict[str, str]) -> bool:
        """Upload files to deployment"""
        try:
            data = {
                "deployment_id": deployment_id,
                "files": files
            }
            response = self._make_request("POST", f"{self.endpoints['deployments']}/{deployment_id}/files", data=data)
            return response.get("success", False)
        except Exception as e:
            logger.error(f"Failed to upload files: {e}")
            return False

class NosanaDeploymentManager:
    """High-level deployment manager for Nosana"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = NosanaClient(api_key)
        self.active_deployments = {}
    
    def deploy_telegram_bot(self, project_name: str = "telegram-manager-bot",
                           environment_vars: Optional[Dict[str, str]] = None) -> Optional[str]:
        """Deploy Telegram Manager Bot to Nosana"""
        
        # Default environment variables
        default_env = {
            "PYTHONPATH": "/app",
            "NODE_ENV": "production"
        }
        
        if environment_vars:
            default_env.update(environment_vars)
        
        # Create deployment configuration
        config = NosanaDeploymentConfig(
            name=project_name,
            description="Telegram Manager Bot with AI backends",
            docker_image="python:3.9-slim",
            gpu_model="RTX 3090",
            gpu_memory="24GB",
            cpu_cores=8,
            ram_gb=32,
            storage_gb=100,
            ports=[8000],
            environment_vars=default_env,
            startup_command="./start.sh",
            restart_policy="always"
        )
        
        # Deploy the application
        deployment_id = self.client.deploy_application(config)
        
        if deployment_id:
            self.active_deployments[deployment_id] = {
                "name": project_name,
                "config": config,
                "created_at": datetime.now()
            }
            logger.info(f"Telegram bot deployment initiated: {deployment_id}")
        
        return deployment_id
    
    async def deploy_telegram_bot_async(self, project_name: str = "telegram-manager-bot",
                                      environment_vars: Optional[Dict[str, str]] = None) -> Optional[str]:
        """Async version of deploy_telegram_bot"""
        
        # Default environment variables
        default_env = {
            "PYTHONPATH": "/app",
            "NODE_ENV": "production"
        }
        
        if environment_vars:
            default_env.update(environment_vars)
        
        # Create deployment configuration
        config = NosanaDeploymentConfig(
            name=project_name,
            description="Telegram Manager Bot with AI backends",
            docker_image="python:3.9-slim",
            gpu_model="RTX 3090",
            gpu_memory="24GB",
            cpu_cores=8,
            ram_gb=32,
            storage_gb=100,
            ports=[8000],
            environment_vars=default_env,
            startup_command="./start.sh",
            restart_policy="always"
        )
        
        # Deploy the application
        deployment_id = await self.client.deploy_application_async(config)
        
        if deployment_id:
            self.active_deployments[deployment_id] = {
                "name": project_name,
                "config": config,
                "created_at": datetime.now()
            }
            logger.info(f"Telegram bot deployment initiated: {deployment_id}")
        
        return deployment_id
    
    def monitor_deployment(self, deployment_id: str) -> Optional[NosanaDeploymentStatus]:
        """Monitor deployment status"""
        return self.client.wait_for_deployment(deployment_id)
    
    def get_deployment_url(self, deployment_id: str) -> Optional[str]:
        """Get deployment URL"""
        status = self.client.get_deployment_status(deployment_id)
        return status.url if status else None
    
    def cleanup_deployment(self, deployment_id: str) -> bool:
        """Clean up deployment"""
        success = self.client.delete_deployment(deployment_id)
        if success and deployment_id in self.active_deployments:
            del self.active_deployments[deployment_id]
        return success

def main():
    """Example usage of Nosana client"""
    print("🚀 Nosana SDK Client Example")
    print("=" * 40)
    
    # Initialize client
    try:
        client = NosanaClient()
        print("✅ Nosana client initialized")
        
        # Test connection
        if client.test_connection():
            print("✅ Connection to Nosana API successful")
        else:
            print("❌ Connection to Nosana API failed")
            return
        
        # Get available GPUs
        gpus = client.get_available_gpus()
        print(f"📊 Available GPUs: {len(gpus)}")
        for gpu in gpus[:3]:  # Show first 3
            print(f"   - {gpu.get('model', 'Unknown')} ({gpu.get('memory', 'Unknown')})")
        
        # Get projects
        projects = client.get_projects()
        print(f"📁 Projects: {len(projects)}")
        
        # Get billing info
        billing = client.get_billing_info()
        print(f"💰 Billing: {billing.get('balance', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure NOSANA_API_KEY is set in your environment")

if __name__ == "__main__":
    main() 