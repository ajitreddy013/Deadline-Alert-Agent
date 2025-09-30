#!/usr/bin/env python3
"""
Startup script for the Deadline Reminder backend server
"""
import uvicorn

if __name__ == "__main__":
    print("Starting Deadline Reminder Backend Server...")
    print("Backend will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    
    uvicorn.run(
        "app:app", 
        host="127.0.0.1", 
        port=8000, 
        reload=True,
        log_level="info"
    )
