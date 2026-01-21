"""
Generic AWI Execution Tool

Provides a single, task-agnostic tool for executing AWI API calls.
The LLM decides all parameters based on:
- Task requirements
- Available operations from manifest
- Endpoint structure from base URL
"""

import logging
import json
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from browser_use.agent.views import ActionResult

logger = logging.getLogger(__name__)


class AWIExecuteAction(BaseModel):
    """
    Generic AWI API execution action.

    All parameters are determined by the LLM based on:
    - The user's task
    - Available operations from the AWI manifest
    - The API structure discovered from the manifest
    """

    operation: str = Field(
        description=(
            'The operation type from the AWI manifest (e.g., read, write, list, get, create, search, delete). '
            'This should match one of the allowed_operations from the manifest.'
        )
    )

    endpoint: str = Field(
        description=(
            'The API endpoint path relative to base URL (e.g., /posts, /posts/{id}, /posts/{id}/comments). '
            'The LLM should construct this based on the task and API structure.'
        )
    )

    method: str = Field(
        description=(
            'HTTP method to use: GET, POST, PUT, PATCH, DELETE. '
            'The LLM should choose based on the operation type and semantic meaning.'
        )
    )

    params: Optional[Dict[str, Any]] = Field(
        default=None,
        description=(
            'Optional query parameters as key-value pairs (e.g., {"sort": "popular", "limit": 3}). '
            'Used for filtering, sorting, pagination, etc. The LLM decides based on task requirements.'
        )
    )

    body: Optional[Dict[str, Any]] = Field(
        default=None,
        description=(
            'Request body as JSON object for POST/PUT/PATCH requests. '
            'REQUIRED for create operations - do NOT send empty {}. '
            'Examples: '
            '- For comments: {"content": "Great post!", "authorName": "Agent"} '
            '- For posts: {"title": "My Title", "content": "Post content here"} '
            '- For search: {"query": "technology", "limit": 5}'
        )
    )


async def awi_execute(
    params: AWIExecuteAction,
    awi_manager
) -> ActionResult:
    """
    Execute a generic AWI API call.

    This is a task-agnostic function that executes whatever API call
    the LLM has planned based on the task and manifest.

    Args:
        params: Execution parameters decided by the LLM
        awi_manager: AWI manager instance with authentication

    Returns:
        ActionResult with the API response formatted for the agent
    """
    try:
        logger.info(
            f"AWI Execute: {params.method} {params.endpoint} "
            f"(operation: {params.operation})"
        )

        # Validate body for POST/PUT/PATCH operations
        if params.method.upper() in ['POST', 'PUT', 'PATCH']:
            logger.info(f"🔍 Checking body for {params.method}: body={params.body}, type={type(params.body)}, is_empty={params.body is None or (isinstance(params.body, dict) and len(params.body) == 0)}")

            if params.body is None or (isinstance(params.body, dict) and len(params.body) == 0):
                # AUTO-FIX: Smart defaults for common operations
                # This helps LLMs that struggle with filling body parameters
                if '/comments' in params.endpoint and params.operation == 'create':
                    # Comment creation - auto-fill with generic content
                    params.body = {
                        'content': 'Great post!',
                        'authorName': 'Agent'
                    }
                    logger.warning(f"⚠️  Auto-filled empty body for comment creation: {params.body}")
                elif params.operation == 'create' and '/posts' in params.endpoint and '/comments' not in params.endpoint:
                    # Post creation - return error (needs specific content)
                    error_msg = (
                        f"❌ Cannot create a post with empty body.\n\n"
                        f"Required fields: title, content\n"
                        f"Example: body={{'title': 'My Post', 'content': 'Post content here'}}"
                    )
                    logger.error(f"❌ Empty body for post creation: {error_msg}")
                    return ActionResult(error=error_msg)
                elif params.operation == 'search':
                    # Search operation - return error (needs query)
                    error_msg = (
                        f"❌ Cannot search with empty body.\n\n"
                        f"Required field: query\n"
                        f"Example: body={{'query': 'search term', 'limit': 10}}"
                    )
                    logger.error(f"❌ Empty body for search: {error_msg}")
                    return ActionResult(error=error_msg)
                else:
                    # Generic error for other operations
                    error_msg = (
                        f"❌ Cannot execute {params.method} {params.endpoint} with empty body.\n\n"
                        f"💡 You MUST provide a body parameter for {params.method} requests.\n\n"
                        f"Current operation: {params.operation}\n"
                        f"Retry with a proper body parameter!"
                    )
                    logger.error(f"❌ Empty body detected: {error_msg}")
                    return ActionResult(error=error_msg)

        # Construct full URL
        base_url = awi_manager.base_url
        # Handle both cases: base_url with/without trailing slash
        if base_url.endswith('/') and params.endpoint.startswith('/'):
            url = base_url + params.endpoint[1:]
        elif not base_url.endswith('/') and not params.endpoint.startswith('/'):
            url = base_url + '/' + params.endpoint
        else:
            url = base_url + params.endpoint

        # Get authentication headers
        headers = awi_manager._get_headers()

        # Make the HTTP request
        async with awi_manager.session.request(
            method=params.method.upper(),
            url=url,
            params=params.params,
            json=params.body,
            headers=headers
        ) as response:

            # Get response status
            status = response.status

            # Try to parse JSON response
            try:
                data = await response.json()
            except Exception:
                # If not JSON, get text
                data = {'text': await response.text(), 'status': status}

            # Check for errors
            if status >= 400:
                error_msg = data.get('error', data.get('message', f'HTTP {status}'))

                # If there are detailed validation errors, include them
                detailed_error = error_msg
                fix_suggestion = ""

                if 'errors' in data and data['errors']:
                    # Format validation errors for the LLM
                    validation_details = []
                    missing_fields = []

                    for err in data['errors']:
                        field = err.get('field', 'unknown')
                        message = err.get('message', 'validation failed')
                        validation_details.append(f"{field}: {message}")

                        # Track missing required fields
                        if 'required' in message.lower():
                            missing_fields.append(field)

                    detailed_error = f"{error_msg}. Details: {'; '.join(validation_details)}"

                    # Add explicit fix suggestion for missing fields
                    if missing_fields:
                        if 'content' in missing_fields:
                            fix_suggestion = f"\n\n💡 FIX: You sent body={{}}. Change it to body={{'content': 'Great post!', 'authorName': 'Agent'}} to include the required 'content' field."
                        else:
                            example_body = {field: f"<{field}_value>" for field in missing_fields}
                            fix_suggestion = f"\n\n💡 FIX: Include these required fields in your body parameter: {example_body}"

                elif 'details' in data and data['details']:
                    # Alternative format (errorsByField)
                    validation_details = []
                    for field, messages in data['details'].items():
                        # Handle both list and string messages
                        if isinstance(messages, (list, tuple)):
                            validation_details.append(f"{field}: {', '.join(messages)}")
                        else:
                            validation_details.append(f"{field}: {messages}")
                    detailed_error = f"{error_msg}. Details: {'; '.join(validation_details)}"

                logger.error(f"❌ AWI Execute failed: {detailed_error}")
                return ActionResult(
                    error=f"API call failed ({status}): {detailed_error}{fix_suggestion}"
                )

            # Format successful response for agent
            formatted = f"✅ API Call Successful ({status} {params.method} {params.endpoint})\n\n"
            formatted += f"Operation: {params.operation}\n"

            # Format response data readably
            if isinstance(data, dict):
                # Pretty print the response
                formatted += "\nResponse:\n"
                formatted += json.dumps(data, indent=2, ensure_ascii=False)
            else:
                formatted += f"\nResponse: {data}\n"

            logger.info(f"✅ AWI Execute successful: {status} {params.method} {params.endpoint}")

            return ActionResult(
                extracted_content=formatted,
                metadata={
                    'response': data,
                    'status': status,
                    'operation': params.operation,
                    'endpoint': params.endpoint,
                    'method': params.method
                }
            )

    except Exception as e:
        logger.error(f"❌ AWI Execute exception: {e}")
        return ActionResult(
            error=f"Failed to execute AWI call: {str(e)}"
        )
