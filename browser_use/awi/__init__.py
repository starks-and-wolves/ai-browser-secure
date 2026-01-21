"""
AWI (Agent Web Interface) Mode for Browser-Use

This module enables browser-use to automatically discover and interact with
AWI-compliant websites using structured APIs instead of DOM parsing.

Benefits:
- 500x token reduction compared to DOM parsing
- Structured responses with semantic metadata
- Session state management for multi-step workflows
- Trajectory tracking for debugging and RL
- Explicit security policies and rate limits
"""

from .discovery import AWIDiscovery
from .manager import AWIManager
from .permission_dialog import AWIPermissionDialog
from .generic_tool import AWIExecuteAction, awi_execute

__all__ = [
    'AWIDiscovery',
    'AWIManager',
    'AWIPermissionDialog',
    'AWIExecuteAction',
    'awi_execute',
]
