"""
Agent Registry for AWI Credential Management

Provides persistent storage and management of AWI agent credentials,
enabling agent reuse across runs without re-registration.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from browser_use.config import AgentCredentialEntry, CONFIG, DBStyleConfigJSON, load_and_migrate_config

logger = logging.getLogger(__name__)


class AgentRegistry:
	"""
	Centralized registry for managing AWI agent credentials.

	Features:
	- Persistent credential storage
	- Agent reuse across sessions
	- Credential lifecycle management
	- Multi-agent support per domain
	- Automatic credential rotation
	"""

	def __init__(self, config_path: Optional[Path] = None):
		"""
		Initialize agent registry.

		Args:
			config_path: Optional path to config file. If not provided, uses default location.
		"""
		if config_path is None:
			config_path = Path(CONFIG.BROWSER_USE_CONFIG_PATH) if CONFIG.BROWSER_USE_CONFIG_PATH else (
				Path(CONFIG.XDG_CONFIG_HOME) / 'browseruse' / 'config.json'
			).expanduser().resolve()

		self.config_path = config_path
		self._config: Optional[DBStyleConfigJSON] = None

	def _load_config(self) -> DBStyleConfigJSON:
		"""Load configuration from disk."""
		if self._config is None:
			self._config = load_and_migrate_config(self.config_path)
		return self._config

	def _save_config(self) -> None:
		"""Save configuration to disk."""
		if self._config is None:
			return

		self.config_path.parent.mkdir(parents=True, exist_ok=True)
		with open(self.config_path, 'w') as f:
			json.dump(self._config.model_dump(), f, indent=2)
		logger.debug(f'Saved agent credentials to {self.config_path}')

	def _normalize_domain(self, url_or_domain: str) -> str:
		"""
		Normalize URL or domain for consistent lookup.

		Args:
			url_or_domain: URL or domain string

		Returns:
			Normalized domain (host:port)
		"""
		# If it looks like a full URL, parse it
		if '://' in url_or_domain:
			parsed = urlparse(url_or_domain)
			domain = parsed.netloc or parsed.path
		else:
			domain = url_or_domain

		# Remove trailing slashes and normalize
		return domain.strip().rstrip('/').lower()

	def store_credentials(
		self,
		agent_id: str,
		agent_name: str,
		domain: str,
		api_key: str,
		permissions: list[str],
		awi_name: str = '',
		description: Optional[str] = None,
		agent_type: str = 'browser-use',
		framework: str = 'python',
		expires_at: Optional[str] = None,
		manifest_version: Optional[str] = None,
		notes: Optional[str] = None,
	) -> AgentCredentialEntry:
		"""
		Store agent credentials in the registry.

		Args:
			agent_id: Unique agent ID from AWI registration
			agent_name: Human-readable agent name
			domain: Domain where agent is registered
			api_key: API key for authentication
			permissions: List of granted permissions
			awi_name: Name of the AWI service
			description: Optional agent description
			agent_type: Type of agent
			framework: Framework used
			expires_at: Optional expiration timestamp
			manifest_version: AWI manifest version
			notes: User notes

		Returns:
			Created AgentCredentialEntry
		"""
		config = self._load_config()

		# Normalize domain
		normalized_domain = self._normalize_domain(domain)

		# Create credential entry
		credential = AgentCredentialEntry(
			agent_id=agent_id,
			agent_name=agent_name,
			domain=normalized_domain,
			awi_name=awi_name,
			api_key=api_key,
			permissions=permissions,
			description=description,
			agent_type=agent_type,
			framework=framework,
			expires_at=expires_at,
			manifest_version=manifest_version,
			notes=notes,
			created_at=datetime.utcnow().isoformat(),
		)

		# Use agent_id as the key (guaranteed unique)
		config.agent_credentials[agent_id] = credential
		self._config = config
		self._save_config()

		logger.info(f'✅ Stored credentials for agent {agent_name} ({agent_id}) at {normalized_domain}')
		return credential

	def get_credentials(self, domain: str, agent_name: Optional[str] = None) -> Optional[AgentCredentialEntry]:
		"""
		Get credentials for a domain, optionally filtered by agent name.

		Args:
			domain: Domain to look up
			agent_name: Optional agent name filter

		Returns:
			AgentCredentialEntry if found and valid, None otherwise
		"""
		config = self._load_config()
		normalized_domain = self._normalize_domain(domain)

		# Find matching credentials
		matches = [
			cred for cred in config.agent_credentials.values()
			if cred.domain == normalized_domain and cred.is_active and not cred.is_expired()
		]

		if not matches:
			logger.debug(f'No active credentials found for domain: {normalized_domain}')
			return None

		# If agent_name specified, filter by name
		if agent_name:
			matches = [cred for cred in matches if cred.agent_name == agent_name]
			if not matches:
				logger.debug(f'No credentials found for agent {agent_name} at {normalized_domain}')
				return None

		# Return most recently used or created
		matches.sort(key=lambda c: c.last_used or c.created_at, reverse=True)
		credential = matches[0]

		logger.info(f'✅ Found credentials for agent {credential.agent_name} at {normalized_domain}')
		return credential

	def get_credentials_by_id(self, agent_id: str) -> Optional[AgentCredentialEntry]:
		"""
		Get credentials by agent ID.

		Args:
			agent_id: Agent ID to look up

		Returns:
			AgentCredentialEntry if found, None otherwise
		"""
		config = self._load_config()
		credential = config.agent_credentials.get(agent_id)

		if credential and credential.is_active and not credential.is_expired():
			return credential

		return None

	def update_last_used(self, agent_id: str) -> bool:
		"""
		Update the last used timestamp for an agent.

		Args:
			agent_id: Agent ID to update

		Returns:
			True if updated successfully, False otherwise
		"""
		config = self._load_config()
		credential = config.agent_credentials.get(agent_id)

		if not credential:
			return False

		credential.update_last_used()
		self._config = config
		self._save_config()

		logger.debug(f'Updated last_used for agent {agent_id}')
		return True

	def deactivate_credentials(self, agent_id: str) -> bool:
		"""
		Deactivate credentials (mark as inactive without deleting).

		Args:
			agent_id: Agent ID to deactivate

		Returns:
			True if deactivated, False if not found
		"""
		config = self._load_config()
		credential = config.agent_credentials.get(agent_id)

		if not credential:
			return False

		credential.is_active = False
		self._config = config
		self._save_config()

		logger.info(f'Deactivated credentials for agent {agent_id}')
		return True

	def delete_credentials(self, agent_id: str) -> bool:
		"""
		Permanently delete credentials from registry.

		Args:
			agent_id: Agent ID to delete

		Returns:
			True if deleted, False if not found
		"""
		config = self._load_config()

		if agent_id not in config.agent_credentials:
			return False

		del config.agent_credentials[agent_id]
		self._config = config
		self._save_config()

		logger.info(f'Deleted credentials for agent {agent_id}')
		return True

	def list_credentials(
		self,
		domain: Optional[str] = None,
		active_only: bool = True
	) -> list[AgentCredentialEntry]:
		"""
		List all stored credentials, optionally filtered.

		Args:
			domain: Optional domain filter
			active_only: Only return active credentials

		Returns:
			List of AgentCredentialEntry objects
		"""
		config = self._load_config()
		credentials = list(config.agent_credentials.values())

		# Apply filters
		if domain:
			normalized_domain = self._normalize_domain(domain)
			credentials = [c for c in credentials if c.domain == normalized_domain]

		if active_only:
			credentials = [c for c in credentials if c.is_active and not c.is_expired()]

		# Sort by last_used (most recent first)
		credentials.sort(key=lambda c: c.last_used or c.created_at, reverse=True)

		return credentials

	def cleanup_expired(self) -> int:
		"""
		Remove expired credentials from registry.

		Returns:
			Number of credentials removed
		"""
		config = self._load_config()
		initial_count = len(config.agent_credentials)

		# Remove expired credentials
		config.agent_credentials = {
			agent_id: cred
			for agent_id, cred in config.agent_credentials.items()
			if not cred.is_expired()
		}

		removed_count = initial_count - len(config.agent_credentials)

		if removed_count > 0:
			self._config = config
			self._save_config()
			logger.info(f'Removed {removed_count} expired credential(s)')

		return removed_count

	def rotate_credentials(
		self,
		agent_id: str,
		new_api_key: str,
		new_permissions: Optional[list[str]] = None
	) -> bool:
		"""
		Rotate credentials for an existing agent.

		Args:
			agent_id: Agent ID to update
			new_api_key: New API key
			new_permissions: Optional new permissions list

		Returns:
			True if rotated successfully, False otherwise
		"""
		config = self._load_config()
		credential = config.agent_credentials.get(agent_id)

		if not credential:
			return False

		credential.api_key = new_api_key
		if new_permissions is not None:
			credential.permissions = new_permissions

		credential.update_last_used()
		self._config = config
		self._save_config()

		logger.info(f'Rotated credentials for agent {agent_id}')
		return True

	def has_credentials(self, domain: str) -> bool:
		"""
		Check if any active credentials exist for a domain.

		Args:
			domain: Domain to check

		Returns:
			True if credentials exist, False otherwise
		"""
		return self.get_credentials(domain) is not None


# Create singleton instance
agent_registry = AgentRegistry()


__all__ = ['AgentRegistry', 'agent_registry', 'AgentCredentialEntry']
