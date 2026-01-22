"""
FastAPI Demo Server for Browser-Use
Serves pre-recorded demos and provides live execution capabilities
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
	title="Browser-Use Demo Server",
	description="API for browser-use demo UI",
	version="0.1.0"
)

# Build allowed origins list
allowed_origins = [
	"http://localhost:3000",  # Local dev
	"http://127.0.0.1:3000",
	"http://localhost:3001",  # Local dev (alternate port)
	"http://127.0.0.1:3001",
	"https://*.repl.co",  # Replit domains (all subdomains)
	"https://*.vercel.app",  # Vercel deployments
	"https://*.onrender.com",  # Render deployments
]

# Add custom frontend URL from environment if provided
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
	allowed_origins.append(frontend_url)
	logger.info(f"Added custom frontend URL to CORS: {frontend_url}")

# Configure CORS
app.add_middleware(
	CORSMiddleware,
	allow_origin_regex=r"https://.*\.repl\.co|https://.*\.vercel\.app|https://.*\.onrender\.com|http://localhost:\d+|http://127\.0\.0\.1:\d+",
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# Import routers
from browser_use.demo_server.routers import live

# Register routers
app.include_router(live.router, prefix="/api/live", tags=["live"])

@app.get("/")
async def root():
	"""Health check endpoint"""
	return {
		"status": "ok",
		"message": "Browser-Use Demo Server",
		"version": "0.1.0"
	}

@app.get("/health")
async def health():
	"""Health check endpoint"""
	return {"status": "healthy"}

if __name__ == "__main__":
	import uvicorn
	uvicorn.run(
		"browser_use.demo_server.main:app",
		host="0.0.0.0",
		port=8000,
		reload=True
	)
