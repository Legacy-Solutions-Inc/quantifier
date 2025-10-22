#!/usr/bin/env python3
"""
Simple health check script for Railway deployment
"""

from fastapi import FastAPI
import uvicorn
import os

app = FastAPI(title="RSB Combinator Health Check")

@app.get("/")
async def root():
    return {"message": "RSB Combinator API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "rsb-combinator"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
