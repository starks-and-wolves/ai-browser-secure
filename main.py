"""
Entry point for browser-use backend
Runs the FastAPI demo server on Replit, Render, or other platforms
"""
import sys
import os
import asyncio

# Windows-specific fix (not needed on Linux, but doesn't hurt)
if sys.platform == 'win32':
	asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Set environment
os.environ['BROWSER_USE_LOGGING_LEVEL'] = 'info'

# Get port from environment (Replit/Render sets this automatically)
port = int(os.getenv('PORT', 8000))

# Detect platform
is_replit = os.getenv('REPL_ID') is not None
is_render = os.getenv('RENDER') is not None

print(f"🚀 Starting browser-use demo server on port {port}")

if is_replit:
	print(f"📍 Environment: Replit")
	print(f"🌐 Access at: https://{os.getenv('REPL_SLUG', 'browser-use-backend')}.{os.getenv('REPL_OWNER', 'your-username')}.repl.co")
elif is_render:
	print(f"📍 Environment: Render")
	render_url = os.getenv('RENDER_EXTERNAL_URL', 'https://your-app.onrender.com')
	print(f"🌐 Access at: {render_url}")
else:
	print(f"📍 Environment: Local/Other")
	print(f"🌐 Access at: http://localhost:{port}")

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
