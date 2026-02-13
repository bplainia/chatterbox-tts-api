#!/usr/bin/env python3
"""
Chatterbox TTS API Entry Point

This is the main entry point for the application.
It imports the FastAPI app from the organized app package.
"""

import os
import asyncio
import uvicorn
from app.main import app
from app.config import Config
from app.core.wyoming_server import start_wyoming_server


async def run_servers():
    """Run both FastAPI and Wyoming servers concurrently"""
    
    # Wyoming server setup
    wyoming_host = os.getenv("WYOMING_HOST", "0.0.0.0")
    wyoming_port = int(os.getenv("WYOMING_PORT", "10200"))
    default_voice = os.getenv("DEFAULT_VOICE", "default")
    
    # FastAPI server setup
    config = uvicorn.Config(
        "app.main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=False,
        access_log=True
    )
    fastapi_server = uvicorn.Server(config)
    
    print("🎙️ Starting Wyoming Protocol server...")
    print(f"   Host: {wyoming_host}:{wyoming_port}")
    print(f"   Default voice: {default_voice}")
    print(f"🌐 Starting OpenAI-compatible API server...")
    print(f"   Host: {Config.HOST}:{Config.PORT}")
    print(f"   API docs: http://{Config.HOST}:{Config.PORT}/docs")
    
    # Run both servers concurrently
    await asyncio.gather(
        start_wyoming_server(wyoming_host, wyoming_port, default_voice),
        fastapi_server.serve()
    )


def main():
    """Main entry point"""
    try:
        Config.validate()
        
        # Check if Wyoming should be enabled
        enable_wyoming = os.getenv("ENABLE_WYOMING", "false").lower() == "true"
        
        if enable_wyoming:
            print("🚀 Starting both OpenAI API and Wyoming Protocol servers...")
            asyncio.run(run_servers())
        else:
            print("🌐 Starting OpenAI API server only...")
            print(f"Server will run on http://{Config.HOST}:{Config.PORT}")
            print(f"API documentation available at http://{Config.HOST}:{Config.PORT}/docs")
            
            uvicorn.run(
                "app.main:app",
                host=Config.HOST,
                port=Config.PORT,
                reload=False,
                access_log=True
            )
    except Exception as e:
        print(f"Failed to start server: {e}")
        exit(1)


if __name__ == "__main__":
    main()