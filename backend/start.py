#!/usr/bin/env python3
"""
Quick start script for the chatbot backend
"""
import os
import sys
import subprocess

def check_groq_key():
    """Check if Groq API key is configured"""
    if not os.path.exists('.env'):
        print("❌ No .env file found!")
        print("📝 Please copy .env.example to .env and add your Groq API key")
        return False
    
    with open('.env', 'r') as f:
        content = f.read()
        if 'your_groq_api_key_here' in content or 'GROQ_API_KEY=' not in content:
            print("❌ Groq API key not configured!")
            print("📝 Please edit .env and add your actual Groq API key")
            return False
    
    print("✅ Groq API key configured")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True, text=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting FastAPI server...")
    print("📡 Server will be available at: http://localhost:8000")
    print("🔄 Make sure your React app is running on port 8080, 5173, or 3000")
    print("⚡ Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "-m", "uvicorn", "main:app", 
                       "--reload", "--host", "0.0.0.0", "--port", "8000"])
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

def main():
    print("🤖 AI Chatbot Backend Setup")
    print("=" * 30)
    
    # Check if we're in the right directory
    if not os.path.exists('main.py'):
        print("❌ Please run this script from the backend directory")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Check Groq API key
    if not check_groq_key():
        sys.exit(1)
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()