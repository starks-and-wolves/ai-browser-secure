"""
AWI Manager

Manages AWI API interactions after agent registration:
- Registers agent with selected permissions
- Stores API key and session information
- Makes API calls instead of DOM parsing
- Manages session state
- Tracks trajectory
"""

import logging
from typing import Dict, Any, Optional, List
import aiohttp
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class AWIManager:
    """Manages AWI API interactions for registered agents."""

    def __init__(
        self,
        manifest: Dict[str, Any],
        session: Optional[aiohttp.ClientSession] = None,
        discovery_url: Optional[str] = None
    ):
        """
        Initialize AWI manager with manifest.

        Args:
            manifest: AWI manifest from discovery
            session: Optional aiohttp session (will create one if not provided)
            discovery_url: Optional URL where manifest was discovered (used as fallback base_url)
        """
        self.manifest = manifest
        self.session = session
        self._own_session = session is None

        # Extract endpoint information
        self.endpoints = manifest.get('endpoints', {})
        self.base_url = self.endpoints.get('base', '')

        # Fallback: use discovery URL if base_url is not in manifest
        if not self.base_url and discovery_url:
            # Extract base URL from discovery URL (remove path)
            from urllib.parse import urlparse
            parsed = urlparse(discovery_url)
            self.base_url = f"{parsed.scheme}://{parsed.netloc}"
            logger.info(f"Using discovery URL as base: {self.base_url}")

        self.auth_info = manifest.get('authentication', {})

        # Agent registration info
        self.agent_info: Optional[Dict[str, Any]] = None
        self.api_key: Optional[str] = None
        self.session_id: Optional[str] = None

        logger.info(f"AWI Manager initialized for: {manifest.get('awi', {}).get('name', 'Unknown')}")

    async def __aenter__(self):
        if self._own_session:
            self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._own_session and self.session:
            await self.session.close()

    async def register_agent(
        self,
        agent_name: str,
        permissions: List[str],
        description: Optional[str] = None,
        agent_type: str = "browser-use",
        framework: str = "python"
    ) -> Dict[str, Any]:
        """
        Register agent with AWI and get API key.

        Args:
            agent_name: Name for the agent
            permissions: List of requested permissions (e.g., ['read', 'write'])
            description: Optional agent description
            agent_type: Type of agent
            framework: Framework being used

        Returns:
            Agent registration response

        Raises:
            Exception if registration fails
        """
        registration_url = self.auth_info.get('registration', {})
        if isinstance(registration_url, dict):
            registration_url = registration_url.get('endpoint')

        if not registration_url:
            raise ValueError("No registration endpoint found in manifest")

        payload = {
            'name': agent_name,
            'permissions': permissions,
            'agentType': agent_type,
            'framework': framework
        }

        if description:
            payload['description'] = description

        logger.info(f"Registering agent: {agent_name} with permissions: {permissions}")

        try:
            async with self.session.post(
                registration_url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status != 201:
                    error_text = await response.text()
                    raise Exception(f"Registration failed ({response.status}): {error_text}")

                data = await response.json()

                if not data.get('success'):
                    raise Exception(f"Registration failed: {data.get('error', 'Unknown error')}")

                # Store agent info
                self.agent_info = data.get('agent', {})
                self.api_key = self.agent_info.get('apiKey')

                if not self.api_key:
                    raise Exception("No API key returned from registration")

                logger.info(f"✅ Agent registered successfully: {self.agent_info.get('id')}")
                return self.agent_info

        except Exception as e:
            logger.error(f"❌ Agent registration failed: {e}")
            raise

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers with authentication."""
        if not self.api_key:
            raise ValueError("Agent not registered. Call register_agent() first.")

        header_name = self.auth_info.get('headerName', self.auth_info.get('header', 'X-Agent-API-Key'))

        return {
            header_name: self.api_key,
            'Content-Type': 'application/json'
        }

    async def list_posts(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
        tag: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List blog posts using AWI API.

        Args:
            page: Page number
            limit: Items per page
            search: Search query
            tag: Filter by tag
            category: Filter by category

        Returns:
            API response with posts and metadata
        """
        endpoint = f"{self.base_url}/posts" if not self.base_url.endswith('/') else f"{self.base_url}posts"

        params = {'page': page, 'limit': limit}
        if search:
            params['search'] = search
        if tag:
            params['tag'] = tag
        if category:
            params['category'] = category

        async with self.session.get(
            endpoint,
            params=params,
            headers=self._get_headers()
        ) as response:
            response.raise_for_status()
            data = await response.json()

            # Extract session ID if present
            if '_sessionState' in data:
                self.session_id = data['_sessionState'].get('sessionId')

            return data

    async def get_post(self, post_id: str) -> Dict[str, Any]:
        """
        Get a single post by ID.

        Args:
            post_id: Post ID

        Returns:
            API response with post data
        """
        endpoint = f"{self.base_url}/posts/{post_id}"

        async with self.session.get(
            endpoint,
            headers=self._get_headers()
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def create_post(
        self,
        title: str,
        content: str,
        author_name: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new blog post.

        Args:
            title: Post title
            content: Post content (HTML allowed, will be sanitized)
            author_name: Author name
            category: Post category
            tags: List of tags

        Returns:
            API response with created post
        """
        endpoint = f"{self.base_url}/posts"

        payload = {
            'title': title,
            'content': content
        }

        if author_name:
            payload['authorName'] = author_name
        if category:
            payload['category'] = category
        if tags:
            payload['tags'] = tags

        async with self.session.post(
            endpoint,
            json=payload,
            headers=self._get_headers()
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def list_comments(self, post_id: str) -> Dict[str, Any]:
        """
        Get comments for a post.

        Args:
            post_id: Post ID

        Returns:
            API response with comments
        """
        endpoint = f"{self.base_url}/posts/{post_id}/comments"

        async with self.session.get(
            endpoint,
            headers=self._get_headers()
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def create_comment(
        self,
        post_id: str,
        content: str,
        author_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a comment to a post.

        Args:
            post_id: Post ID
            content: Comment content (HTML allowed, will be sanitized)
            author_name: Author name

        Returns:
            API response with created comment
        """
        endpoint = f"{self.base_url}/posts/{post_id}/comments"

        payload = {'content': content}
        if author_name:
            payload['authorName'] = author_name

        async with self.session.post(
            endpoint,
            json=payload,
            headers=self._get_headers()
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def search(
        self,
        query: str,
        intent: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Advanced search with natural language.

        Args:
            query: Search query
            intent: Search intent
            filters: Additional filters

        Returns:
            API response with search results
        """
        endpoint = f"{self.base_url}/search"

        payload = {'query': query}
        if intent:
            payload['intent'] = intent
        if filters:
            payload['filters'] = filters

        async with self.session.post(
            endpoint,
            json=payload,
            headers=self._get_headers()
        ) as response:
            response.raise_for_status()
            return await response.json()

    # Session State Management

    async def get_session_state(self) -> Dict[str, Any]:
        """
        Get current session state.

        Returns:
            Complete session state snapshot
        """
        session_endpoints = self.manifest.get('features', {}).get('session_state', {}).get('endpoints', {})
        state_endpoint = session_endpoints.get('state')

        if not state_endpoint:
            raise ValueError("Session state endpoint not available")

        async with self.session.get(
            state_endpoint,
            headers=self._get_headers()
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def get_action_history(
        self,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get action history (trajectory trace).

        Args:
            limit: Number of recent actions to return
            offset: Offset from most recent

        Returns:
            Action history with trajectory
        """
        session_endpoints = self.manifest.get('features', {}).get('session_state', {}).get('endpoints', {})
        history_endpoint = session_endpoints.get('history')

        if not history_endpoint:
            raise ValueError("Action history endpoint not available")

        params = {'limit': limit, 'offset': offset}

        async with self.session.get(
            history_endpoint,
            params=params,
            headers=self._get_headers()
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def get_state_diff(self) -> Dict[str, Any]:
        """
        Get state diff since last action (incremental update).

        Returns:
            State differences
        """
        session_endpoints = self.manifest.get('features', {}).get('session_state', {}).get('endpoints', {})
        diff_endpoint = session_endpoints.get('diff')

        if not diff_endpoint:
            raise ValueError("State diff endpoint not available")

        async with self.session.get(
            diff_endpoint,
            headers=self._get_headers()
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def end_session(self) -> Dict[str, Any]:
        """
        End current session and get statistics.

        Returns:
            Session statistics
        """
        session_endpoints = self.manifest.get('features', {}).get('session_state', {}).get('endpoints', {})
        end_endpoint = session_endpoints.get('end')

        if not end_endpoint:
            raise ValueError("End session endpoint not available")

        async with self.session.post(
            end_endpoint,
            headers=self._get_headers()
        ) as response:
            response.raise_for_status()
            return await response.json()

    def is_registered(self) -> bool:
        """Check if agent is registered."""
        return self.api_key is not None

    def get_agent_info(self) -> Optional[Dict[str, Any]]:
        """Get registered agent information."""
        return self.agent_info

    def get_session_id(self) -> Optional[str]:
        """Get current session ID."""
        return self.session_id
