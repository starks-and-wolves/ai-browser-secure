"""
AWI Discovery Module

Discovers AWI capabilities from websites using multiple methods:
1. HTTP headers (X-AWI-Discovery)
2. Well-known URI (/.well-known/llm-text)
3. Capabilities endpoint (/api/agent/capabilities)
"""

import logging
from typing import Optional, Dict, Any
from urllib.parse import urljoin
import aiohttp

logger = logging.getLogger(__name__)


class AWIDiscovery:
    """Discovers and parses AWI manifests from websites."""

    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        self.session = session
        self._own_session = session is None

    async def __aenter__(self):
        if self._own_session:
            self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._own_session and self.session:
            await self.session.close()

    async def discover(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Discover AWI manifest from a URL using multiple methods.

        Args:
            url: Base URL to check for AWI

        Returns:
            AWI manifest dictionary or None if not found
        """
        logger.info(f"🔍 Discovering AWI at {url}...")

        # Normalize the discovery URL (remove trailing slashes, ensure scheme)
        discovery_url = url.rstrip('/')
        if not discovery_url.startswith(('http://', 'https://')):
            discovery_url = f'https://{discovery_url}'

        # Method 1: Check HTTP headers
        manifest = await self._discover_via_headers(discovery_url)
        if manifest:
            logger.info("✅ AWI discovered via HTTP headers")
            return self._normalize_manifest_urls(manifest, discovery_url)

        # Method 2: Try well-known URI
        manifest = await self._discover_via_well_known(discovery_url)
        if manifest:
            logger.info("✅ AWI discovered via .well-known/llm-text")
            return self._normalize_manifest_urls(manifest, discovery_url)

        # Method 3: Try capabilities endpoint
        manifest = await self._discover_via_capabilities(discovery_url)
        if manifest:
            logger.info("✅ AWI discovered via capabilities endpoint")
            return self._normalize_manifest_urls(manifest, discovery_url)

        logger.warning(f"❌ No AWI found at {url}")
        return None

    async def _discover_via_headers(self, url: str) -> Optional[Dict[str, Any]]:
        """Discover AWI via HTTP response headers."""
        try:
            async with self.session.head(url, allow_redirects=True) as response:
                # Check for AWI discovery header
                awi_discovery = response.headers.get('X-AWI-Discovery')
                if not awi_discovery:
                    return None

                # Fetch the manifest from the discovery URL
                manifest_url = urljoin(url, awi_discovery)
                return await self._fetch_manifest(manifest_url)

        except Exception as e:
            logger.debug(f"Header discovery failed: {e}")
            return None

    async def _discover_via_well_known(self, url: str) -> Optional[Dict[str, Any]]:
        """Discover AWI via .well-known/llm-text URI."""
        well_known_url = urljoin(url, '/.well-known/llm-text')
        return await self._fetch_manifest(well_known_url)

    async def _discover_via_capabilities(self, url: str) -> Optional[Dict[str, Any]]:
        """Discover AWI via /api/agent/capabilities endpoint."""
        capabilities_url = urljoin(url, '/api/agent/capabilities')
        manifest = await self._fetch_manifest(capabilities_url)

        # If we get capabilities response, check if it has wellKnownUri for full manifest
        if manifest and 'capabilities' in manifest:
            caps = manifest['capabilities']
            if 'discovery' in caps and 'wellKnownUri' in caps['discovery']:
                # Fetch the full manifest from wellKnownUri
                full_manifest_url = caps['discovery']['wellKnownUri']
                full_manifest = await self._fetch_manifest(full_manifest_url)
                if full_manifest:
                    return full_manifest

        return manifest

    async def _fetch_manifest(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch and parse AWI manifest from URL."""
        try:
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    # Handle both application/json and other content types
                    # Some servers serve .well-known files as application/octet-stream
                    try:
                        manifest = await response.json()
                    except aiohttp.ContentTypeError:
                        # Try parsing as text then JSON
                        text = await response.text()
                        import json
                        manifest = json.loads(text)

                    # Validate manifest has required fields
                    if self._validate_manifest(manifest):
                        return manifest
                return None
        except Exception as e:
            logger.debug(f"Failed to fetch manifest from {url}: {e}")
            return None

    def _validate_manifest(self, manifest: Dict[str, Any]) -> bool:
        """Validate that manifest has required AWI fields."""
        # Check for either full manifest or capabilities response
        has_awi_section = 'awi' in manifest or 'capabilities' in manifest
        has_endpoints = 'endpoints' in manifest or 'operations' in manifest

        if not has_awi_section and not has_endpoints:
            logger.debug("Invalid manifest: missing required fields")
            return False

        return True

    def _normalize_manifest_urls(self, manifest: Dict[str, Any], actual_url: str) -> Dict[str, Any]:
        """
        Replace localhost URLs in manifest with the actual discovered URL.

        This fixes backend manifests that have hardcoded localhost URLs
        but are deployed to production domains.

        Args:
            manifest: The AWI manifest
            actual_url: The actual URL where AWI was discovered

        Returns:
            Manifest with normalized URLs
        """
        import copy
        import re
        from urllib.parse import urlparse

        # Deep copy to avoid modifying original
        normalized = copy.deepcopy(manifest)

        # Parse the actual URL to extract scheme and netloc
        actual_parsed = urlparse(actual_url)
        actual_base = f"{actual_parsed.scheme}://{actual_parsed.netloc}"

        # Patterns to match localhost URLs
        localhost_patterns = [
            r'http://localhost:\d+',
            r'https://localhost:\d+',
            r'http://127\.0\.0\.1:\d+',
            r'https://127\.0\.0\.1:\d+',
        ]

        def replace_localhost(obj):
            """Recursively replace localhost URLs in nested dict/list structures."""
            if isinstance(obj, dict):
                return {k: replace_localhost(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_localhost(item) for item in obj]
            elif isinstance(obj, str):
                # Check if this string contains a localhost URL
                for pattern in localhost_patterns:
                    if re.match(pattern, obj):
                        # Replace localhost with actual domain
                        logger.debug(
                            f"Replacing localhost URL: {obj} -> {actual_base}...")
                        # Replace the host part but keep the path
                        obj = re.sub(pattern, actual_base, obj)
                return obj
            else:
                return obj

        # Count replacements for logging
        before_str = str(manifest)
        after_normalized = replace_localhost(normalized)
        after_str = str(after_normalized)

        if before_str != after_str:
            localhost_count = before_str.count('localhost')
            logger.info(
                f"🔧 Normalized {localhost_count} localhost URLs to {actual_base}")

        return after_normalized

    def extract_capabilities(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract capability information from manifest.

        Returns:
            Dictionary with:
            - allowed_operations: List of allowed operations
            - disallowed_operations: List of disallowed operations
            - security_features: List of security features
            - rate_limits: Rate limit configuration
            - permissions: Available permission levels
        """
        capabilities = {}

        # Handle both full manifest and capabilities-only response
        if 'capabilities' in manifest:
            cap_section = manifest['capabilities']
        else:
            cap_section = manifest

        # Extract capability directives
        capabilities['allowed_operations'] = cap_section.get(
            'allowed_operations', [])
        capabilities['disallowed_operations'] = cap_section.get(
            'disallowed_operations', [])
        capabilities['security_features'] = cap_section.get(
            'security_features', [])
        capabilities['rate_limits'] = cap_section.get('rate_limits', {})
        capabilities['confirmation_required'] = cap_section.get(
            'confirmation_required', [])
        capabilities['response_features'] = cap_section.get(
            'response_features', [])
        capabilities['session_management'] = cap_section.get(
            'session_management', [])

        return capabilities

    def extract_authentication(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract authentication information from manifest.

        Returns:
            Dictionary with:
            - type: Authentication type (e.g., 'bearer', 'api-key')
            - header: Header name for authentication
            - registration: Registration endpoint
            - permissions: Available permission levels
        """
        auth_info = manifest.get('authentication', {})

        return {
            'type': auth_info.get('type', 'bearer'),
            'scheme': auth_info.get('scheme', 'api-key'),
            'header': auth_info.get('headerName', auth_info.get('header', 'X-Agent-API-Key')),
            'registration': auth_info.get('registration', {}).get('endpoint', auth_info.get('registration')),
            'permissions': auth_info.get('permissions', {})
        }

    def extract_endpoints(self, manifest: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract API endpoints from manifest.

        Returns:
            Dictionary mapping endpoint names to URLs
        """
        return manifest.get('endpoints', {})

    def extract_operations(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract available operations from manifest.

        Returns:
            Dictionary mapping operation categories to operation details
        """
        # Handle both nested operations and flat capabilities
        if 'operations' in manifest:
            return manifest['operations']
        elif 'capabilities' in manifest and 'operations' in manifest['capabilities']:
            return manifest['capabilities']['operations']
        return {}

    def get_summary(self, manifest: Dict[str, Any]) -> str:
        """
        Generate human-readable summary of AWI capabilities.

        Returns:
            Formatted string summary
        """
        capabilities = self.extract_capabilities(manifest)
        auth = self.extract_authentication(manifest)

        summary = []
        summary.append("🎯 AWI Discovered")
        summary.append(
            f"   Name: {manifest.get('awi', {}).get('name', 'Unknown')}")
        summary.append(
            f"   Version: {manifest.get('awi', {}).get('version', 'Unknown')}")

        summary.append("\n✅ Allowed Operations:")
        for op in capabilities.get('allowed_operations', [])[:5]:
            summary.append(f"   • {op}")

        summary.append("\n🚫 Disallowed Operations:")
        for op in capabilities.get('disallowed_operations', [])[:5]:
            summary.append(f"   • {op}")

        summary.append("\n🔒 Security Features:")
        for feature in capabilities.get('security_features', [])[:5]:
            summary.append(f"   • {feature}")

        summary.append(f"\n🔑 Authentication: {auth['type']}")
        summary.append(f"   Header: {auth['header']}")

        perms = auth.get('permissions', {})
        if perms:
            available = perms.get('available', [])
            default = perms.get('default', [])
            summary.append(f"   Available Permissions: {', '.join(available)}")
            summary.append(f"   Default Permissions: {', '.join(default)}")

        return '\n'.join(summary)
