#!/usr/bin/env python3
"""
Atoma Client for Telegram Manager Bot
Provides access to distributed compute power through the Atoma DePIN network
"""

import os
import json
import requests
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import asyncio

try:
    import aiohttp
except ImportError:
    aiohttp = None
    print("⚠️  aiohttp not installed. Async features will be disabled.")

@dataclass
class Usage:
    """Mock usage object to maintain compatibility with OpenAI response format"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

@dataclass
class Choice:
    """Mock choice object to maintain compatibility with OpenAI response format"""
    message: Dict[str, str]

@dataclass
class AtomaResponse:
    """Mock response object to maintain compatibility with OpenAI response format"""
    choices: List[Choice]
    usage: Usage

class AtomaClient:
    """Client for interacting with Atoma DePIN network"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.atoma.ai", 
                 model: str = "llama3.2", timeout: int = 120):
        self.api_key = api_key or os.getenv("ATOMA_API_KEY")
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = timeout
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            })
    
    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to the Atoma API"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Atoma API request failed: {e}")
    
    async def _make_async_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make an async request to the Atoma API"""
        if aiohttp is None:
            raise Exception("aiohttp not installed. Install it with: pip install aiohttp")
            
        url = f"{self.base_url}{endpoint}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=self.session.headers, timeout=self.timeout) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            raise Exception(f"Atoma API async request failed: {e}")
    
    def chat_completions_create(self, messages: List[Dict[str, str]], 
                              temperature: float = 0.6,
                              max_tokens: Optional[int] = None) -> AtomaResponse:
        """
        Create a chat completion using Atoma DePIN network
        Maintains compatibility with OpenAI's chat.completions.create method
        """
        # Convert messages to Atoma format
        prompt = self._format_messages_for_atoma(messages)
        
        # Prepare request data
        request_data = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "stream": False
        }
        
        if max_tokens:
            request_data["max_tokens"] = max_tokens
        
        # Make request
        response_data = self._make_request("/v1/chat/completions", request_data)
        
        # Extract response
        if "choices" not in response_data or not response_data["choices"]:
            raise Exception("Invalid response from Atoma API")
        
        choice_data = response_data["choices"][0]
        usage_data = response_data.get("usage", {})
        
        # Create mock response object for compatibility
        choice = Choice(message=choice_data.get("message", {"content": ""}))
        usage = Usage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0)
        )
        
        return AtomaResponse(choices=[choice], usage=usage)
    
    async def chat_completions_create_async(self, messages: List[Dict[str, str]], 
                                          temperature: float = 0.6,
                                          max_tokens: Optional[int] = None) -> AtomaResponse:
        """
        Async version of chat_completions_create
        """
        # Convert messages to Atoma format
        prompt = self._format_messages_for_atoma(messages)
        
        # Prepare request data
        request_data = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "stream": False
        }
        
        if max_tokens:
            request_data["max_tokens"] = max_tokens
        
        # Make async request
        response_data = await self._make_async_request("/v1/chat/completions", request_data)
        
        # Extract response
        if "choices" not in response_data or not response_data["choices"]:
            raise Exception("Invalid response from Atoma API")
        
        choice_data = response_data["choices"][0]
        usage_data = response_data.get("usage", {})
        
        # Create mock response object for compatibility
        choice = Choice(message=choice_data.get("message", {"content": ""}))
        usage = Usage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0)
        )
        
        return AtomaResponse(choices=[choice], usage=usage)
    
    def _format_messages_for_atoma(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI message format to Atoma prompt format"""
        formatted_prompt = ""
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                formatted_prompt += f"System: {content}\n\n"
            elif role == "user":
                formatted_prompt += f"User: {content}\n"
            elif role == "assistant":
                formatted_prompt += f"Assistant: {content}\n"
        
        formatted_prompt += "Assistant: "
        return formatted_prompt
    
    def list_models(self) -> List[str]:
        """List available models on Atoma network"""
        try:
            response = self.session.get(f"{self.base_url}/v1/models")
            response.raise_for_status()
            data = response.json()
            return [model["id"] for model in data.get("data", [])]
        except requests.exceptions.RequestException:
            return []
    
    def get_network_status(self) -> Dict[str, Any]:
        """Get Atoma network status and available compute"""
        try:
            response = self.session.get(f"{self.base_url}/v1/network/status")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {"error": "Could not fetch network status"}
    
    def test_connection(self) -> bool:
        """Test if Atoma API is accessible"""
        try:
            response = self.session.get(f"{self.base_url}/v1/models", timeout=10)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics and costs"""
        try:
            response = self.session.get(f"{self.base_url}/v1/usage")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {"error": "Could not fetch usage stats"}

# Global client instance
atoma_client = None

def initialize_atoma_client(api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
    """Initialize the global Atoma client"""
    global atoma_client
    
    # Get configuration from environment or use defaults
    api_key = api_key or os.getenv("ATOMA_API_KEY")
    base_url = base_url or os.getenv("ATOMA_BASE_URL", "https://api.atoma.ai")
    model = model or os.getenv("ATOMA_MODEL", "llama3.2")
    
    if not api_key:
        raise Exception("ATOMA_API_KEY not found. Please set it in your environment or .env file.")
    
    atoma_client = AtomaClient(api_key=api_key, base_url=base_url, model=model)
    
    # Test connection
    if not atoma_client.test_connection():
        raise Exception(f"Could not connect to Atoma API at {base_url}. Check your API key and network connection.")
    
    print(f"✅ Connected to Atoma DePIN network at {base_url}")
    print(f"📦 Using model: {model}")
    
    # Get network status
    try:
        status = atoma_client.get_network_status()
        if "error" not in status:
            print(f"🌐 Network status: {status.get('status', 'unknown')}")
            print(f"💻 Available compute: {status.get('available_compute', 'unknown')}")
    except Exception as e:
        print(f"⚠️  Could not fetch network status: {e}")
    
    # List available models
    available_models = atoma_client.list_models()
    if available_models:
        print(f"📋 Available models: {', '.join(available_models)}")

def get_atoma_client() -> AtomaClient:
    """Get the global Atoma client instance"""
    if atoma_client is None:
        raise Exception("Atoma client not initialized. Call initialize_atoma_client() first.")
    return atoma_client

async def get_atoma_client_async() -> AtomaClient:
    """Get the global Atoma client instance (async version)"""
    if atoma_client is None:
        raise Exception("Atoma client not initialized. Call initialize_atoma_client() first.")
    return atoma_client 