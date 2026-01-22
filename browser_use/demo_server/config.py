"""
Configuration settings for the demo server
"""

import os
from typing import List

class Settings:
	# Server configuration
	HOST: str = os.getenv("HOST", "0.0.0.0")
	PORT: int = int(os.getenv("PORT", "8000"))

	# CORS origins (comma-separated in env)
	CORS_ORIGINS: List[str] = os.getenv(
		"CORS_ORIGINS",
		"http://localhost:3000,http://127.0.0.1:3000"
	).split(",")

	# Demo storage
	DEMO_STORAGE_PATH: str = os.getenv("DEMO_STORAGE_PATH", "./demos")

	# Rate limiting
	MAX_SESSIONS_PER_IP: int = int(os.getenv("MAX_SESSIONS_PER_IP", "10"))
	SESSION_TIMEOUT_SECONDS: int = int(os.getenv("SESSION_TIMEOUT_SECONDS", "300"))  # 5 minutes

	# Security
	ALLOWED_DOMAINS: List[str] = os.getenv(
		"ALLOWED_DOMAINS",
		"google.com,github.com,reddit.com"
	).split(",")

settings = Settings()
