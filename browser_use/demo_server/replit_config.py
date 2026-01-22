"""
Browser configuration optimized for Replit deployment
Reduces memory footprint and CPU usage for free tier constraints
"""
import os
from browser_use.browser.profile import BrowserProfile


def get_replit_browser_profile() -> BrowserProfile:
	"""
	Get optimized browser profile for Replit deployment.

	This configuration:
	- Runs in headless mode (required for server deployment)
	- Disables unnecessary features to reduce memory usage
	- Uses minimal Chrome arguments for better performance
	- Suitable for Replit's 512MB RAM free tier

	Returns:
		BrowserProfile configured for Replit
	"""
	# Check if running on Replit
	is_replit = os.getenv('REPL_ID') is not None

	# Lightweight Chrome arguments for limited resources
	optimized_args = [
		'--disable-dev-shm-usage',  # Use /tmp instead of /dev/shm (limited in containers)
		'--no-sandbox',  # Required for containerized environments
		'--disable-setuid-sandbox',
		'--disable-gpu',  # No GPU in server environment
		'--disable-software-rasterizer',
		'--disable-extensions',  # No extensions needed
		'--disable-background-networking',
		'--disable-background-timer-throttling',
		'--disable-backgrounding-occluded-windows',
		'--disable-breakpad',  # Disable crash reporting
		'--disable-component-extensions-with-background-pages',
		'--disable-features=TranslateUI,BlinkGenPropertyTrees',
		'--disable-ipc-flooding-protection',
		'--disable-renderer-backgrounding',
		'--enable-features=NetworkService,NetworkServiceInProcess',
		'--force-color-profile=srgb',
		'--hide-scrollbars',
		'--metrics-recording-only',
		'--mute-audio',  # No audio needed
		'--no-first-run',
		'--no-default-browser-check',
		'--disable-sync',  # No Google account sync
	]

	# Additional memory optimization for Replit
	if is_replit:
		optimized_args.extend([
			'--memory-pressure-off',
			'--max-old-space-size=256',  # Limit V8 heap size
		])

	profile = BrowserProfile(
		headless=True,  # Must be headless on server
		disable_security=False,  # Keep security enabled
		extra_chromium_args=optimized_args,
	)

	return profile


def should_use_remote_browser() -> bool:
	"""
	Determine if we should use a remote browser service instead of local Chromium.

	Returns True if:
	- Running on Replit free tier (limited resources)
	- BROWSERLESS_TOKEN environment variable is set

	Returns:
		bool: Whether to use remote browser
	"""
	is_replit = os.getenv('REPL_ID') is not None
	has_browserless_token = bool(os.getenv('BROWSERLESS_TOKEN'))

	return is_replit and has_browserless_token


def get_remote_browser_url() -> str | None:
	"""
	Get remote browser WebSocket URL if configured.

	Returns:
		str | None: WebSocket URL for remote browser, or None if not configured
	"""
	token = os.getenv('BROWSERLESS_TOKEN')
	if token:
		return f"wss://chrome.browserless.io?token={token}"
	return None
