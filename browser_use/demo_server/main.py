"""
FastAPI Demo Server for Browser-Use
Serves pre-recorded demos and provides live execution capabilities
"""

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

# Configure CORS
app.add_middleware(
	CORSMiddleware,
	allow_origins=[
		"http://localhost:3000",  # Next.js dev server
		"http://127.0.0.1:3000",
		"http://localhost:3001",  # Next.js dev server (alternate port)
		"http://127.0.0.1:3001",
		# Add production origins here when deploying
	],
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
