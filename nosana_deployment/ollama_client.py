#!/usr/bin/env python3
"""
Ollama Client for Telegram Manager Bot
Replaces OpenAI API with local Ollama models
"""

import os
import json
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

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
class OllamaResponse:
    """Mock response object to maintain compatibility with OpenAI response format"""
    choices: List[Choice]
    usage: Usage

class OllamaClient:
    """Client for interacting with local Ollama models"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2"):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.session = requests.Session()
    
    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to the Ollama API"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.post(url, json=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama API request failed: {e}")
    
    def chat_completions_create(self, messages: List[Dict[str, str]], 
                              temperature: float = 0.6,
                              max_tokens: Optional[int] = None) -> OllamaResponse:
        """
        Create a chat completion using Ollama
        Maintains compatibility with OpenAI's chat.completions.create method
        """
        # Convert OpenAI format to Ollama format
        prompt = self._format_messages_for_ollama(messages)
        
        # Prepare request data
        request_data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        if max_tokens:
            request_data["options"]["num_predict"] = max_tokens
        
        # Make request
        response_data = self._make_request("/api/generate", request_data)
        
        # Extract response
        if "response" not in response_data:
            raise Exception("Invalid response from Ollama API")
        
        # Create mock response object for compatibility
        choice = Choice(message={"content": response_data["response"]})
        usage = Usage(
            prompt_tokens=response_data.get("prompt_eval_count", 0),
            completion_tokens=response_data.get("eval_count", 0),
            total_tokens=response_data.get("prompt_eval_count", 0) + response_data.get("eval_count", 0)
        )
        
        return OllamaResponse(choices=[choice], usage=usage)
    
    def _format_messages_for_ollama(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI message format to Ollama prompt format"""
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
        """List available models"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        except requests.exceptions.RequestException:
            return []
    
    def test_connection(self) -> bool:
        """Test if Ollama is running and accessible"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

# Global client instance
ollama_client = None

def initialize_ollama_client(model: Optional[str] = None, base_url: Optional[str] = None):
    """Initialize the global Ollama client"""
    global ollama_client
    
    # Get configuration from environment or use defaults
    model = model or os.getenv("OLLAMA_MODEL", "llama3.2")
    base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    ollama_client = OllamaClient(base_url=base_url, model=model)
    
    # Test connection
    if not ollama_client.test_connection():
        raise Exception(f"Could not connect to Ollama at {base_url}. Make sure Ollama is running.")
    
    print(f"✅ Connected to Ollama at {base_url}")
    print(f"📦 Using model: {model}")
    
    # List available models
    available_models = ollama_client.list_models()
    if available_models:
        print(f"📋 Available models: {', '.join(available_models)}")

def get_ollama_client() -> OllamaClient:
    """Get the global Ollama client instance"""
    if ollama_client is None:
        raise Exception("Ollama client not initialized. Call initialize_ollama_client() first.")
    return ollama_client 