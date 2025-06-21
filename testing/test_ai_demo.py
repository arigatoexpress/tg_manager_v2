#!/usr/bin/env python3
"""
Ultimate AI Demo: Interactive, Multi-Backend, Model Selection, Prompt Templates, Performance Stats, and Robust Error Handling
"""

import time
import os
import sys
import psutil
import json
from typing import Optional

# Import both clients
from ollama_client import initialize_ollama_client, get_ollama_client
try:
    from atoma_client import initialize_atoma_client, get_atoma_client
    atoma_available = True
except ImportError:
    atoma_available = False

BACKENDS = ["Ollama"]
if atoma_available:
    BACKENDS.append("Atoma")

PROMPT_TEMPLATES = [
    ("Professional Email", "Write a professional email to schedule a meeting with a client about a new project. Include specific details about the agenda and next steps."),
    ("Summarize Messages", "Summarize these messages, identify key priorities, and suggest specific follow-up actions with deadlines."),
    ("Daily Briefing", "Generate a clear, actionable daily briefing that combines insights from notes and chat summaries."),
    ("Translate to French", "Translate the following text to French: {text}"),
    ("Code Explanation", "Explain what the following code does: {code}"),
    ("Custom", None)
]

LOG_FILE = "ai_demo_results.jsonl"

def get_system_info():
    """Get system information for performance analysis"""
    print("🖥️  System Information")
    print("=" * 50)
    cpu_count = psutil.cpu_count()
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f"💻 CPU: {cpu_count} cores, {cpu_percent}% usage")
    memory = psutil.virtual_memory()
    memory_gb = memory.total / (1024**3)
    memory_used_gb = memory.used / (1024**3)
    memory_percent = memory.percent
    print(f"🧠 RAM: {memory_gb:.1f}GB total, {memory_used_gb:.1f}GB used ({memory_percent}%)")
    disk = psutil.disk_usage('/')
    disk_gb = disk.total / (1024**3)
    disk_free_gb = disk.free / (1024**3)
    print(f"💾 Disk: {disk_gb:.1f}GB total, {disk_free_gb:.1f}GB free")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print()

def select_backend_and_model():
    print("Select AI backend:")
    for i, backend in enumerate(BACKENDS):
        print(f"  {i+1}. {backend}")
    backend_idx = input(f"Enter backend number [1]: ").strip()
    backend_idx = int(backend_idx) - 1 if backend_idx else 0
    backend = BACKENDS[backend_idx]

    if backend == "Ollama":
        initialize_ollama_client()
        client = get_ollama_client()
        models = client.list_models()
        print("Available Ollama models:")
        for i, m in enumerate(models):
            print(f"  {i+1}. {m}")
        model_idx = input(f"Select model [1]: ").strip()
        model_idx = int(model_idx) - 1 if model_idx else 0
        model = models[model_idx] if models else "llama3.2"
        # Re-initialize with selected model
        initialize_ollama_client(model=model)
        client = get_ollama_client()
    elif backend == "Atoma":
        initialize_atoma_client()
        client = get_atoma_client()
        models = client.list_models()
        print("Available Atoma models:")
        for i, m in enumerate(models):
            print(f"  {i+1}. {m}")
        model_idx = input(f"Select model [1]: ").strip()
        model_idx = int(model_idx) - 1 if model_idx else 0
        model = models[model_idx] if models else "llama3.2"
        initialize_atoma_client(model=model)
        client = get_atoma_client()
    else:
        raise Exception("Unknown backend")
    print(f"✅ Using backend: {backend}, model: {model}")
    return backend, model, client

def select_prompt():
    print("\nPrompt Templates:")
    for i, (name, _) in enumerate(PROMPT_TEMPLATES):
        print(f"  {i+1}. {name}")
    idx = input(f"Select prompt template [1]: ").strip()
    idx = int(idx) - 1 if idx else 0
    name, template = PROMPT_TEMPLATES[idx]
    if name == "Custom":
        prompt = input("Enter your custom prompt: ")
    elif "{text}" in (template or ""):
        text = input("Enter text to translate: ")
        prompt = template.format(text=text)
    elif "{code}" in (template or ""):
        code = input("Paste code to explain: ")
        prompt = template.format(code=code)
    else:
        prompt = template
    return name, prompt

def analyze_response_time(start_time, end_time, task_name):
    duration = end_time - start_time
    print(f"⏱️  {task_name} took {duration:.2f} seconds")
    if duration < 2:
        print("   🚀 Excellent performance! Very fast response.")
    elif duration < 5:
        print("   ✅ Good performance! Reasonable response time.")
    elif duration < 10:
        print("   ⚠️  Moderate performance. Consider using a smaller model.")
    else:
        print("   🐌 Slow performance. Your machine might be struggling with this model.")
    print()
    return duration

def log_result(entry):
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def run_demo():
    print("🤖 Ultimate AI Capabilities Demo")
    print("=" * 60)
    get_system_info()
    backend, model, client = select_backend_and_model()
    results = []
    while True:
        name, prompt = select_prompt()
        if not prompt:
            print("No prompt provided. Exiting.")
            break
        print(f"\n📝 Running: {name}")
        print("-" * 50)
        print(f"Prompt: {prompt}")
        pre_cpu = psutil.cpu_percent(interval=1)
        pre_mem = psutil.virtual_memory().percent
        start_time = time.time()
        try:
            response = client.chat_completions_create([
                {"role": "user", "content": prompt}
            ])
            end_time = time.time()
            result = response.choices[0].message["content"]
            usage = getattr(response, "usage", None)
            print(f"\n📋 AI Response:\n{result}\n")
            duration = analyze_response_time(start_time, end_time, name)
            post_cpu = psutil.cpu_percent(interval=1)
            post_mem = psutil.virtual_memory().percent
            print(f"💻 CPU Usage: {pre_cpu}% → {post_cpu}%")
            print(f"🧠 Memory Usage: {pre_mem}% → {post_mem}%")
            if usage:
                print(f"🔢 Token Usage: Prompt={getattr(usage, 'prompt_tokens', '?')}, Completion={getattr(usage, 'completion_tokens', '?')}, Total={getattr(usage, 'total_tokens', '?')}")
            entry = {
                "backend": backend,
                "model": model,
                "prompt_name": name,
                "prompt": prompt,
                "response": result,
                "duration": duration,
                "cpu_before": pre_cpu,
                "cpu_after": post_cpu,
                "mem_before": pre_mem,
                "mem_after": post_mem,
                "usage": usage.__dict__ if usage else None,
                "timestamp": time.time()
            }
            log_result(entry)
            results.append(entry)
        except Exception as e:
            print(f"❌ Error: {e}")
            print("💡 Try a smaller model or different backend if available.")
        again = input("\nRun another prompt? (y/n) [y]: ").strip().lower()
        if again not in ("", "y", "yes"):
            break
    print("\n📈 Demo session complete. Summary:")
    print("=" * 50)
    for i, entry in enumerate(results):
        print(f"{i+1}. {entry['prompt_name']} | {entry['backend']}:{entry['model']} | {entry['duration']:.2f}s")
    print(f"\nResults saved to {LOG_FILE}")
    print("🎉 The bot is ready to use with these capabilities!")

if __name__ == "__main__":
    try:
        run_demo()
    except ImportError as e:
        print(f"❌ Import error: {e}. Installing missing package...")
        import subprocess
        subprocess.check_call(["pip", "install", str(e.name)])
        print(f"✅ {e.name} installed. Please run the script again.")
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        print("💡 Make sure Ollama or Atoma is running and properly configured.") 