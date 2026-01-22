"""
Replit entry point for browser-use backend
This file runs the FastAPI demo server on Replit
"""
import sys
import os
import asyncio

# Windows-specific fix (not needed on Replit Linux, but doesn't hurt)
if sys.platform == 'win32':
	asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Set environment for Replit
os.environ['BROWSER_USE_LOGGING_LEVEL'] = 'info'

# Get port from environment (Replit sets this automatically)
port = int(os.getenv('PORT', 8000))

print(f"🚀 Starting browser-use demo server on port {port}")
print(f"📍 Environment: Replit")
print(f"🌐 Access at: https://{os.getenv('REPL_SLUG', 'browser-use-backend')}.{os.getenv('REPL_OWNER', 'your-username')}.repl.co")

# Run the server
if __name__ == "__main__":
	import uvicorn
	uvicorn.run(
		"browser_use.demo_server.main:app",
		host="0.0.0.0",
		port=port,
		log_level="info",
		access_log=True
	)
