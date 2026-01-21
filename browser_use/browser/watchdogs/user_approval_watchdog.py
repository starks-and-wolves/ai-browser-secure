"""User approval watchdog for intercepting sensitive browser actions.

This watchdog provides IDE-like security prompts for browser agent actions,
requiring user approval before executing potentially dangerous operations like:
- Navigation to new URLs
- Form filling and text input
- Capturing sensitive/PII data
- File uploads/downloads
- Cookie/session manipulation
- Script execution
"""

import asyncio
import re
from collections.abc import Awaitable, Callable
from enum import Enum
from typing import TYPE_CHECKING, Any, ClassVar

from pydantic import Field, PrivateAttr

from browser_use.browser.events import (
	BaseEvent,
	ClickElementEvent,
	FileDownloadedEvent,
	NavigateToUrlEvent,
	SendKeysEvent,
	TypeTextEvent,
	UploadFileEvent,
)
from browser_use.browser.watchdog_base import BaseWatchdog

if TYPE_CHECKING:
	from browser_use.dom.views import EnhancedDOMTreeNode


class SensitiveActionType(str, Enum):
	"""Types of sensitive actions that may require user approval."""

	NAVIGATION = 'navigation'
	FORM_INPUT = 'form_input'
	SENSITIVE_DATA_INPUT = 'sensitive_data_input'
	FILE_UPLOAD = 'file_upload'
	FILE_DOWNLOAD = 'file_download'
	CLICK_SUBMIT = 'click_submit'
	CLICK_LOGIN = 'click_login'
	CLICK_PAYMENT = 'click_payment'
	KEYBOARD_SHORTCUT = 'keyboard_shortcut'


class ApprovalDecision(str, Enum):
	"""User's decision on a sensitive action."""

	APPROVE = 'approve'
	DENY = 'deny'
	APPROVE_ALL_SESSION = 'approve_all_session'
	APPROVE_ALL_DOMAIN = 'approve_all_domain'


class PermissionDeniedError(Exception):
	"""Exception raised when user denies a permission request.

	Contains context about the denied action to help the agent:
	- Skip dependent steps
	- Re-plan if the step was critical
	- Exit if re-planning fails
	"""

	def __init__(
		self,
		message: str,
		action_type: str,
		url: str | None = None,
		current_goal: str | None = None,
		reasoning: str | None = None,
		is_critical: bool = False,
		replan_count: int = 0,
	):
		super().__init__(message)
		self.action_type = action_type
		self.url = url
		self.current_goal = current_goal
		self.reasoning = reasoning
		self.is_critical = is_critical
		self.replan_count = replan_count

	def should_exit(self) -> bool:
		"""Check if the agent should exit after this denial."""
		# Exit if critical step denied and already tried re-planning once
		return self.is_critical and self.replan_count >= 1

	def should_replan(self) -> bool:
		"""Check if the agent should try to re-plan after this denial."""
		# Re-plan if critical step and haven't tried yet
		return self.is_critical and self.replan_count == 0

	def get_replan_context(self) -> str:
		"""Get context string for re-planning prompt."""
		parts = [
			f'Permission denied for action: {self.action_type}',
		]
		if self.url:
			parts.append(f'URL: {self.url}')
		if self.current_goal:
			parts.append(f'Goal: {self.current_goal}')
		if self.reasoning:
			parts.append(f'Reason for step: {self.reasoning}')
		parts.append('Please find an alternative approach that does not require this permission.')
		return '\n'.join(parts)


class ApprovalRequest:
	"""Represents a request for user approval of a sensitive action.

	Enhanced to include:
	- Agent's current plan/goal context
	- Reasoning for why this step is needed
	- Step number and total steps info
	- Task description for context
	"""

	def __init__(
		self,
		action_type: SensitiveActionType,
		description: str,
		details: dict[str, Any],
		risk_level: str = 'medium',
		url: str | None = None,
		element_info: dict[str, Any] | None = None,
		# Enhanced context fields
		task: str | None = None,
		current_goal: str | None = None,
		reasoning: str | None = None,
		memory: str | None = None,
		step_number: int | None = None,
		max_steps: int | None = None,
		all_actions: list[str] | None = None,
		is_critical: bool = False,
	):
		self.action_type = action_type
		self.description = description
		self.details = details
		self.risk_level = risk_level
		self.url = url
		self.element_info = element_info
		# Enhanced context
		self.task = task
		self.current_goal = current_goal
		self.reasoning = reasoning
		self.memory = memory
		self.step_number = step_number
		self.max_steps = max_steps
		self.all_actions = all_actions or []
		self.is_critical = is_critical

	def to_dict(self) -> dict[str, Any]:
		return {
			'action_type': self.action_type.value,
			'description': self.description,
			'details': self.details,
			'risk_level': self.risk_level,
			'url': self.url,
			'element_info': self.element_info,
			'task': self.task,
			'current_goal': self.current_goal,
			'reasoning': self.reasoning,
			'memory': self.memory,
			'step_number': self.step_number,
			'max_steps': self.max_steps,
			'all_actions': self.all_actions,
			'is_critical': self.is_critical,
		}

	def get_cache_key(self) -> str:
		"""Generate a cache key for this request based on action type, URL/target, and reasoning.

		Used to avoid showing duplicate popups for the same action with same reasoning.
		"""
		import hashlib

		key_parts = [
			self.action_type.value,
			self.url or '',
			self.current_goal or '',
			# Include a hash of the reasoning to detect same reasoning
			hashlib.md5((self.reasoning or '').encode()).hexdigest()[:8],
		]
		return '|'.join(key_parts)

	def format_prompt(self) -> str:
		"""Format the approval request as a human-readable prompt."""
		risk_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴', 'critical': '🚨'}.get(self.risk_level, '⚠️')

		lines = [
			f'\n{risk_emoji} SECURITY APPROVAL REQUIRED {risk_emoji}',
			f'Action Type: {self.action_type.value.upper()}',
			f'Description: {self.description}',
			f'Risk Level: {self.risk_level.upper()}',
		]

		# Add step info if available
		if self.step_number is not None:
			step_info = f'Step {self.step_number}'
			if self.max_steps:
				step_info += f' of {self.max_steps}'
			lines.append(f'Progress: {step_info}')

		# Add task context
		if self.task:
			lines.append(f'Task: {self.task[:100]}{"..." if len(self.task) > 100 else ""}')

		# Add current goal
		if self.current_goal:
			lines.append(f'Current Goal: {self.current_goal}')

		# Add reasoning
		if self.reasoning:
			lines.append(f'Why this step: {self.reasoning}')

		if self.url:
			lines.append(f'URL: {self.url}')

		if self.details:
			lines.append('Details:')
			for key, value in self.details.items():
				if key == 'text' and len(str(value)) > 50:
					value = str(value)[:50] + '...'
				lines.append(f'  - {key}: {value}')

		if self.element_info:
			lines.append('Element Info:')
			for key, value in self.element_info.items():
				lines.append(f'  - {key}: {value}')

		# Show all planned actions for this step
		if self.all_actions:
			lines.append('Planned Actions:')
			for i, action in enumerate(self.all_actions, 1):
				lines.append(f'  {i}. {action}')

		if self.is_critical:
			lines.append('⚠️ This step is CRITICAL for completing the task')

		return '\n'.join(lines)


# Patterns for detecting sensitive form fields
SENSITIVE_FIELD_PATTERNS = {
	'password': [r'password', r'passwd', r'pwd', r'pass', r'secret'],
	'credit_card': [r'card.?num', r'cc.?num', r'credit.?card', r'card.?number', r'pan'],
	'cvv': [r'cvv', r'cvc', r'security.?code', r'card.?code'],
	'ssn': [r'ssn', r'social.?security', r'social.?sec'],
	'email': [r'email', r'e-mail', r'mail'],
	'phone': [r'phone', r'tel', r'mobile', r'cell'],
	'address': [r'address', r'street', r'city', r'zip', r'postal'],
	'name': [r'first.?name', r'last.?name', r'full.?name', r'name'],
	'dob': [r'dob', r'birth', r'birthday'],
	'bank': [r'account.?num', r'routing', r'iban', r'swift', r'bank'],
	'api_key': [r'api.?key', r'token', r'secret.?key', r'access.?key'],
	'username': [r'username', r'user.?name', r'login', r'user.?id'],
}

# Patterns for detecting sensitive button/link actions
SENSITIVE_BUTTON_PATTERNS = {
	'submit': [r'submit', r'send', r'confirm', r'complete'],
	'login': [r'login', r'log.?in', r'sign.?in', r'signin', r'authenticate'],
	'payment': [r'pay', r'purchase', r'buy', r'checkout', r'order', r'subscribe'],
	'delete': [r'delete', r'remove', r'cancel', r'terminate'],
	'transfer': [r'transfer', r'send.?money', r'wire'],
}

# High-risk domains that always require approval
HIGH_RISK_DOMAINS = [
	'paypal.com',
	'stripe.com',
	'venmo.com',
	'bank',
	'chase.com',
	'wellsfargo.com',
	'bankofamerica.com',
	'citibank.com',
	'capitalone.com',
	'coinbase.com',
	'binance.com',
	'kraken.com',
	'robinhood.com',
	'fidelity.com',
	'schwab.com',
	'vanguard.com',
	'etrade.com',
	'ameritrade.com',
]


class UserApprovalWatchdog(BaseWatchdog):
	"""Watchdog that intercepts sensitive browser actions and requests user approval.

	This provides IDE-like security prompts for browser agent actions, protecting against:
	- Prompt injection attacks via malicious DOM content
	- Unintended navigation to phishing sites
	- Unauthorized form submissions with sensitive data
	- Session hijacking attempts
	- Unauthorized file operations

	Configuration:
		- approval_callback: Async function to request user approval
		- auto_approve_safe_actions: Skip approval for clearly safe actions
		- require_approval_for_navigation: Always require approval for navigation
		- require_approval_for_forms: Always require approval for form input
		- require_approval_for_sensitive_data: Require approval for PII/sensitive fields
		- approved_domains: List of pre-approved domains (skip navigation approval)
		- denied_domains: List of always-denied domains
	"""

	LISTENS_TO: ClassVar[list[type[BaseEvent]]] = [
		# NavigateToUrlEvent is handled directly by BrowserSession.on_NavigateToUrlEvent
		# to ensure approval happens BEFORE navigation, not via event bus registration
		TypeTextEvent,
		ClickElementEvent,
		UploadFileEvent,
		SendKeysEvent,
		FileDownloadedEvent,
	]
	EMITS: ClassVar[list[type[BaseEvent]]] = []

	# Configuration fields
	approval_callback: Callable[[ApprovalRequest], Awaitable[ApprovalDecision]] | None = Field(
		default=None, description='Async callback function to request user approval. If None, uses browser UI or console prompts.'
	)
	use_browser_ui: bool = Field(
		default=True, description='Use in-browser UI popup for approval prompts. Falls back to console if browser UI fails.'
	)
	auto_approve_safe_actions: bool = Field(default=True, description='Automatically approve clearly safe actions.')
	require_approval_for_navigation: bool = Field(default=True, description='Require approval for all navigation.')
	require_approval_for_forms: bool = Field(default=False, description='Require approval for all form input.')
	require_approval_for_sensitive_data: bool = Field(
		default=True, description='Require approval when sensitive/PII data is detected.'
	)
	require_approval_for_file_operations: bool = Field(default=True, description='Require approval for file uploads/downloads.')
	approved_domains: list[str] = Field(default_factory=list, description='Pre-approved domains (skip approval).')
	denied_domains: list[str] = Field(default_factory=list, description='Always-denied domains.')
	session_approved_actions: set[str] = Field(default_factory=set, description='Actions approved for the entire session.')
	domain_approved_actions: dict[str, set[str]] = Field(default_factory=dict, description='Actions approved per domain.')

	# Private state
	_approval_lock: asyncio.Lock = PrivateAttr(default_factory=asyncio.Lock)

	# Approval cache: stores decisions keyed by cache_key (action+url+reasoning hash)
	# This prevents showing duplicate popups for the same action with same reasoning
	_approval_cache: dict[str, ApprovalDecision] = PrivateAttr(default_factory=dict)

	# Denied actions cache: tracks denied actions to help agent skip dependent steps
	_denied_actions: list[dict[str, Any]] = PrivateAttr(default_factory=list)

	# Agent context: updated by the agent before each action
	_current_task: str | None = PrivateAttr(default=None)
	_current_goal: str | None = PrivateAttr(default=None)
	_current_reasoning: str | None = PrivateAttr(default=None)
	_current_memory: str | None = PrivateAttr(default=None)
	_current_step: int | None = PrivateAttr(default=None)
	_max_steps: int | None = PrivateAttr(default=None)
	_current_actions: list[str] = PrivateAttr(default_factory=list)

	# Re-plan tracking: count how many times we've tried to re-plan after denial
	_replan_attempts: dict[str, int] = PrivateAttr(default_factory=dict)

	def _get_domain_from_url(self, url: str) -> str | None:
		"""Extract domain from URL."""
		from urllib.parse import urlparse

		try:
			parsed = urlparse(url)
			return parsed.hostname
		except Exception:
			return None

	def _is_domain_approved(self, domain: str | None) -> bool:
		"""Check if domain is in the approved list."""
		if not domain:
			return False
		for approved in self.approved_domains:
			if approved.startswith('*.'):
				if domain.endswith(approved[1:]) or domain == approved[2:]:
					return True
			elif domain == approved or domain.endswith('.' + approved):
				return True
		return False

	def _is_domain_denied(self, domain: str | None) -> bool:
		"""Check if domain is in the denied list."""
		if not domain:
			return False
		for denied in self.denied_domains:
			if denied.startswith('*.'):
				if domain.endswith(denied[1:]) or domain == denied[2:]:
					return True
			elif domain == denied or domain.endswith('.' + denied):
				return True
		return False

	def _is_high_risk_domain(self, domain: str | None) -> bool:
		"""Check if domain is a high-risk financial/sensitive domain."""
		if not domain:
			return False
		domain_lower = domain.lower()
		for risk_domain in HIGH_RISK_DOMAINS:
			if risk_domain in domain_lower:
				return True
		return False

	def update_agent_context(
		self,
		task: str | None = None,
		current_goal: str | None = None,
		reasoning: str | None = None,
		memory: str | None = None,
		step_number: int | None = None,
		max_steps: int | None = None,
		actions: list[str] | None = None,
	) -> None:
		"""Update the agent context for the next approval request.

		Called by the agent before executing actions to provide context
		for the approval popup.
		"""
		if task is not None:
			self._current_task = task
		if current_goal is not None:
			self._current_goal = current_goal
		if reasoning is not None:
			self._current_reasoning = reasoning
		if memory is not None:
			self._current_memory = memory
		if step_number is not None:
			self._current_step = step_number
		if max_steps is not None:
			self._max_steps = max_steps
		if actions is not None:
			self._current_actions = actions

	def _check_approval_cache(self, request: ApprovalRequest) -> ApprovalDecision | None:
		"""Check if we have a cached decision for this request.

		Returns the cached decision if found, None otherwise.
		"""
		cache_key = request.get_cache_key()
		if cache_key in self._approval_cache:
			cached_decision = self._approval_cache[cache_key]
			self.logger.debug(f'Using cached approval decision for {cache_key}: {cached_decision}')
			return cached_decision
		return None

	def _cache_approval_decision(self, request: ApprovalRequest, decision: ApprovalDecision) -> None:
		"""Cache the approval decision for future requests with same key."""
		cache_key = request.get_cache_key()
		self._approval_cache[cache_key] = decision
		self.logger.debug(f'Cached approval decision for {cache_key}: {decision}')

	def _record_denied_action(self, request: ApprovalRequest) -> None:
		"""Record a denied action for smart skip functionality."""
		self._denied_actions.append(
			{
				'action_type': request.action_type.value,
				'url': request.url,
				'description': request.description,
				'current_goal': request.current_goal,
				'reasoning': request.reasoning,
				'timestamp': asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else 0,
			}
		)

	def get_denied_actions(self) -> list[dict[str, Any]]:
		"""Get list of denied actions for the agent to consider when re-planning."""
		return self._denied_actions.copy()

	def clear_denied_actions(self) -> None:
		"""Clear the denied actions list (e.g., after successful re-planning)."""
		self._denied_actions.clear()

	def should_skip_due_to_denial(self, url: str | None = None, action_type: str | None = None) -> bool:
		"""Check if an action should be skipped because a related action was denied.

		This helps the agent skip dependent steps when a critical step was denied.
		"""
		if not self._denied_actions:
			return False

		for denied in self._denied_actions:
			# Skip if same URL was denied
			if url and denied.get('url') == url:
				return True
			# Skip if same action type on same goal was denied
			if action_type and denied.get('action_type') == action_type:
				if self._current_goal and denied.get('current_goal') == self._current_goal:
					return True
		return False

	def get_replan_count(self, goal_key: str) -> int:
		"""Get how many times we've tried to re-plan for a specific goal."""
		return self._replan_attempts.get(goal_key, 0)

	def increment_replan_count(self, goal_key: str) -> int:
		"""Increment and return the re-plan count for a goal."""
		self._replan_attempts[goal_key] = self._replan_attempts.get(goal_key, 0) + 1
		return self._replan_attempts[goal_key]

	def reset_replan_count(self, goal_key: str | None = None) -> None:
		"""Reset re-plan count for a goal or all goals."""
		if goal_key:
			self._replan_attempts.pop(goal_key, None)
		else:
			self._replan_attempts.clear()

	def _detect_sensitive_field_type(self, element_node: 'EnhancedDOMTreeNode') -> tuple[str | None, str]:
		"""Detect if an element is a sensitive form field.

		Returns:
			Tuple of (field_type, risk_level) or (None, 'low') if not sensitive.
		"""
		if not element_node:
			return None, 'low'

		# Get element attributes
		attrs = element_node.attributes or {}
		tag_name = (element_node.tag_name or '').lower()

		# Check input type
		input_type = attrs.get('type', '').lower()
		if input_type == 'password':
			return 'password', 'high'

		# Check name, id, placeholder, aria-label for sensitive patterns
		check_values = [
			attrs.get('name', ''),
			attrs.get('id', ''),
			attrs.get('placeholder', ''),
			attrs.get('aria-label', ''),
			attrs.get('autocomplete', ''),
		]
		combined_text = ' '.join(str(v).lower() for v in check_values if v)

		for field_type, patterns in SENSITIVE_FIELD_PATTERNS.items():
			for pattern in patterns:
				if re.search(pattern, combined_text, re.IGNORECASE):
					risk = 'critical' if field_type in ['password', 'credit_card', 'cvv', 'ssn', 'bank', 'api_key'] else 'high'
					return field_type, risk

		return None, 'low'

	def _detect_sensitive_button_type(self, element_node: 'EnhancedDOMTreeNode') -> tuple[str | None, str]:
		"""Detect if an element is a sensitive button/link.

		Returns:
			Tuple of (button_type, risk_level) or (None, 'low') if not sensitive.
		"""
		if not element_node:
			return None, 'low'

		attrs = element_node.attributes or {}
		tag_name = (element_node.tag_name or '').lower()

		# Get text content and attributes to check
		text_content = element_node.get_all_children_text(max_depth=2) if hasattr(element_node, 'get_all_children_text') else ''
		check_values = [
			text_content,
			attrs.get('value', ''),
			attrs.get('aria-label', ''),
			attrs.get('title', ''),
			attrs.get('name', ''),
			attrs.get('id', ''),
		]
		combined_text = ' '.join(str(v).lower() for v in check_values if v)

		for button_type, patterns in SENSITIVE_BUTTON_PATTERNS.items():
			for pattern in patterns:
				if re.search(pattern, combined_text, re.IGNORECASE):
					risk = 'high' if button_type in ['payment', 'delete', 'transfer'] else 'medium'
					return button_type, risk

		return None, 'low'

	def _get_element_info(self, element_node: 'EnhancedDOMTreeNode') -> dict[str, Any]:
		"""Extract relevant info from an element for the approval prompt."""
		if not element_node:
			return {}

		attrs = element_node.attributes or {}
		return {
			'tag': element_node.tag_name,
			'type': attrs.get('type'),
			'name': attrs.get('name'),
			'id': attrs.get('id'),
			'placeholder': attrs.get('placeholder'),
			'text': element_node.get_all_children_text(max_depth=1)[:100]
			if hasattr(element_node, 'get_all_children_text')
			else None,
		}

	async def _request_approval(self, request: ApprovalRequest) -> ApprovalDecision:
		"""Request user approval for a sensitive action.

		Enhanced with:
		- Approval caching to skip duplicate requests with same reasoning
		- Agent context (task, goal, reasoning) included in request
		- Denied action tracking for smart skip functionality
		"""
		async with self._approval_lock:
			# Enrich request with agent context
			if not request.task:
				request.task = self._current_task
			if not request.current_goal:
				request.current_goal = self._current_goal
			if not request.reasoning:
				request.reasoning = self._current_reasoning
			if not request.memory:
				request.memory = self._current_memory
			if request.step_number is None:
				request.step_number = self._current_step
			if request.max_steps is None:
				request.max_steps = self._max_steps
			if not request.all_actions:
				request.all_actions = self._current_actions

			# Check if already approved for session
			action_key = f'{request.action_type.value}:{request.url or "any"}'
			if action_key in self.session_approved_actions:
				return ApprovalDecision.APPROVE

			# Check if approved for domain
			if request.url:
				domain = self._get_domain_from_url(request.url)
				if domain and domain in self.domain_approved_actions:
					if request.action_type.value in self.domain_approved_actions[domain]:
						return ApprovalDecision.APPROVE

			# Check approval cache (same action + URL + reasoning = skip popup)
			cached_decision = self._check_approval_cache(request)
			if cached_decision is not None:
				if cached_decision == ApprovalDecision.DENY:
					# Re-record denial for tracking
					self._record_denied_action(request)
				return cached_decision

			# Use custom callback if provided
			if self.approval_callback:
				decision = await self.approval_callback(request)
			elif self.use_browser_ui:
				# Default: browser UI popup (falls back to console on error)
				decision = await self._browser_ui_approval_prompt(request)
			else:
				# Console-based approval
				decision = await self._console_approval_prompt(request)

			# Cache the decision for future requests with same key
			self._cache_approval_decision(request, decision)

			# Track denied actions for smart skip functionality
			if decision == ApprovalDecision.DENY:
				self._record_denied_action(request)

			# Handle session/domain-wide approvals
			if decision == ApprovalDecision.APPROVE_ALL_SESSION:
				self.session_approved_actions.add(action_key)
				return ApprovalDecision.APPROVE
			elif decision == ApprovalDecision.APPROVE_ALL_DOMAIN and request.url:
				domain = self._get_domain_from_url(request.url)
				if domain:
					if domain not in self.domain_approved_actions:
						self.domain_approved_actions[domain] = set()
					self.domain_approved_actions[domain].add(request.action_type.value)
				return ApprovalDecision.APPROVE

			return decision

	async def _console_approval_prompt(self, request: ApprovalRequest) -> ApprovalDecision:
		"""Display console prompt for user approval."""
		print(request.format_prompt())
		print('\nOptions:')
		print('  [y] Approve this action')
		print('  [n] Deny this action')
		print('  [s] Approve all similar actions for this session')
		print('  [d] Approve all similar actions for this domain')
		print()

		# Use asyncio to handle input without blocking
		loop = asyncio.get_event_loop()
		try:
			response = await asyncio.wait_for(
				loop.run_in_executor(None, lambda: input('Your choice [y/n/s/d]: ').strip().lower()),
				timeout=300.0,  # 5 minute timeout
			)
		except TimeoutError:
			self.logger.warning('⏱️ Approval request timed out, denying action')
			return ApprovalDecision.DENY

		if response == 'y':
			return ApprovalDecision.APPROVE
		elif response == 's':
			return ApprovalDecision.APPROVE_ALL_SESSION
		elif response == 'd':
			return ApprovalDecision.APPROVE_ALL_DOMAIN
		else:
			return ApprovalDecision.DENY

	async def _browser_ui_approval_prompt(self, request: ApprovalRequest) -> ApprovalDecision:
		"""Display an in-browser UI popup for user approval using CDP."""
		import uuid

		# Check if we're on a page that can display the UI (not about:blank or chrome:// pages)
		is_blank_page = False
		try:
			current_url = ''
			# Get current page URL from browser session
			if self.browser_session.agent_focus_target_id:
				target = self.browser_session.session_manager.get_target(self.browser_session.agent_focus_target_id)
				if target:
					current_url = target.url or ''

			# Check if we're on a blank/chrome page
			if (
				not current_url
				or current_url in ['about:blank', 'chrome://newtab/', 'chrome://new-tab-page/']
				or current_url.startswith('chrome://')
			):
				is_blank_page = True
		except Exception:
			is_blank_page = True

		# Generate unique ID for this approval request
		request_id = str(uuid.uuid4())[:8]

		# Risk level colors and icons
		risk_colors = {
			'low': '#22c55e',  # green
			'medium': '#eab308',  # yellow
			'high': '#ef4444',  # red
			'critical': '#dc2626',  # dark red
		}
		risk_icons = {
			'low': '✓',
			'medium': '⚠',
			'high': '⛔',
			'critical': '🚨',
		}

		risk_color = risk_colors.get(request.risk_level, '#eab308')
		risk_icon = risk_icons.get(request.risk_level, '⚠')

		# Build details HTML
		details_html = ''
		if request.details:
			for key, value in request.details.items():
				if key == 'text' and len(str(value)) > 50:
					value = str(value)[:50] + '...'
				details_html += f'<div class="detail-row"><span class="detail-key">{key}:</span> <span class="detail-value">{value}</span></div>'

		element_html = ''
		if request.element_info:
			element_html = '<div class="section-title">Element Info</div>'
			for key, value in request.element_info.items():
				if value:
					element_html += f'<div class="detail-row"><span class="detail-key">{key}:</span> <span class="detail-value">{value}</span></div>'

		# Build enhanced context HTML (task, goal, reasoning, step info)
		context_html = ''

		# Step progress
		if request.step_number is not None:
			step_text = f'Step {request.step_number}'
			if request.max_steps:
				step_text += f' of {request.max_steps}'
			context_html += f'<div class="step-progress">{step_text}</div>'

		# Task context
		if request.task:
			task_display = request.task[:150] + '...' if len(request.task) > 150 else request.task
			context_html += f'<div class="context-section"><div class="context-label">Task:</div><div class="context-value">{task_display}</div></div>'

		# Current goal
		if request.current_goal:
			context_html += f'<div class="context-section"><div class="context-label">Current Goal:</div><div class="context-value goal-value">{request.current_goal}</div></div>'

		# Reasoning (why this step is needed)
		if request.reasoning:
			context_html += f'<div class="context-section"><div class="context-label">Why this step:</div><div class="context-value reasoning-value">{request.reasoning}</div></div>'

		# Planned actions for this step
		actions_html = ''
		if request.all_actions:
			actions_html = (
				'<div class="actions-section"><div class="section-title">Planned Actions</div><ol class="actions-list">'
			)
			for action in request.all_actions[:5]:  # Limit to 5 actions
				actions_html += f'<li>{action}</li>'
			if len(request.all_actions) > 5:
				actions_html += f'<li>... and {len(request.all_actions) - 5} more</li>'
			actions_html += '</ol></div>'

		# Critical step indicator
		critical_html = ''
		if request.is_critical:
			critical_html = '<div class="critical-badge">⚠️ Critical Step - Required for task completion</div>'

		# JavaScript and CSS for the popup
		popup_js = f"""
(function() {{
    // Remove any existing popup
    const existingPopup = document.getElementById('browser-use-approval-popup');
    if (existingPopup) existingPopup.remove();

    // Create popup container
    const popup = document.createElement('div');
    popup.id = 'browser-use-approval-popup';
    popup.innerHTML = `
        <style>
            #browser-use-approval-popup {{
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.7);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 2147483647;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                backdrop-filter: blur(4px);
            }}
            .approval-dialog {{
                background: #1a1a2e;
                border-radius: 16px;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
                max-width: 480px;
                width: 90%;
                overflow: hidden;
                animation: slideIn 0.3s ease-out;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            @keyframes slideIn {{
                from {{ transform: translateY(-20px); opacity: 0; }}
                to {{ transform: translateY(0); opacity: 1; }}
            }}
            .dialog-header {{
                background: {risk_color};
                color: white;
                padding: 20px 24px;
                display: flex;
                align-items: center;
                gap: 12px;
            }}
            .risk-icon {{
                font-size: 28px;
            }}
            .header-text {{
                flex: 1;
            }}
            .header-title {{
                font-size: 18px;
                font-weight: 600;
                margin: 0;
            }}
            .header-subtitle {{
                font-size: 13px;
                opacity: 0.9;
                margin-top: 4px;
            }}
            .dialog-body {{
                padding: 24px;
                color: #e2e8f0;
            }}
            .action-type {{
                display: inline-block;
                background: rgba(255, 255, 255, 0.1);
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 16px;
            }}
            .description {{
                font-size: 16px;
                line-height: 1.5;
                margin-bottom: 20px;
                color: #f1f5f9;
            }}
            .section-title {{
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                color: #94a3b8;
                margin-bottom: 8px;
                margin-top: 16px;
            }}
            .step-progress {{
                display: inline-block;
                background: rgba(96, 165, 250, 0.2);
                color: #60a5fa;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 500;
                margin-bottom: 12px;
            }}
            .context-section {{
                margin-bottom: 12px;
                padding: 10px 12px;
                background: rgba(0, 0, 0, 0.2);
                border-radius: 8px;
                border-left: 3px solid #3b82f6;
            }}
            .context-label {{
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                color: #94a3b8;
                margin-bottom: 4px;
            }}
            .context-value {{
                font-size: 14px;
                color: #e2e8f0;
                line-height: 1.4;
            }}
            .goal-value {{
                color: #60a5fa;
                font-weight: 500;
            }}
            .reasoning-value {{
                color: #a78bfa;
                font-style: italic;
            }}
            .actions-section {{
                margin-top: 16px;
                padding: 12px;
                background: rgba(0, 0, 0, 0.2);
                border-radius: 8px;
            }}
            .actions-list {{
                margin: 8px 0 0 0;
                padding-left: 20px;
                color: #cbd5e1;
                font-size: 13px;
            }}
            .actions-list li {{
                margin-bottom: 4px;
            }}
            .critical-badge {{
                background: rgba(239, 68, 68, 0.2);
                color: #ef4444;
                padding: 8px 12px;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 500;
                text-align: center;
                margin-bottom: 16px;
                border: 1px solid rgba(239, 68, 68, 0.3);
            }}
            .detail-row {{
                font-size: 14px;
                padding: 6px 0;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }}
            .detail-key {{
                color: #94a3b8;
            }}
            .detail-value {{
                color: #e2e8f0;
                word-break: break-all;
            }}
            .url-display {{
                background: rgba(0, 0, 0, 0.3);
                padding: 10px 14px;
                border-radius: 8px;
                font-size: 13px;
                color: #60a5fa;
                word-break: break-all;
                margin-bottom: 16px;
            }}
            .dialog-footer {{
                padding: 16px 24px 24px;
                display: flex;
                flex-direction: column;
                gap: 10px;
            }}
            .btn-row {{
                display: flex;
                gap: 10px;
            }}
            .btn {{
                flex: 1;
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s;
            }}
            .btn:hover {{
                transform: translateY(-1px);
            }}
            .btn-approve {{
                background: #22c55e;
                color: white;
            }}
            .btn-approve:hover {{
                background: #16a34a;
            }}
            .btn-deny {{
                background: #ef4444;
                color: white;
            }}
            .btn-deny:hover {{
                background: #dc2626;
            }}
            .btn-secondary {{
                background: rgba(255, 255, 255, 0.1);
                color: #e2e8f0;
                font-size: 13px;
                padding: 10px 16px;
            }}
            .btn-secondary:hover {{
                background: rgba(255, 255, 255, 0.15);
            }}
            .timer {{
                text-align: center;
                font-size: 12px;
                color: #64748b;
                margin-top: 8px;
            }}
        </style>
        <div class="approval-dialog">
            <div class="dialog-header">
                <span class="risk-icon">{risk_icon}</span>
                <div class="header-text">
                    <h2 class="header-title">Security Approval Required</h2>
                    <div class="header-subtitle">Risk Level: {request.risk_level.upper()}</div>
                </div>
            </div>
            <div class="dialog-body">
                {context_html}
                {critical_html}
                <div class="action-type">{request.action_type.value.replace('_', ' ')}</div>
                <div class="description">{request.description}</div>
                {"<div class='url-display'>" + (request.url or '') + '</div>' if request.url else ''}
                {actions_html}
                {"<div class='section-title'>Details</div>" + details_html if details_html else ''}
                {element_html}
            </div>
            <div class="dialog-footer">
                <div class="btn-row">
                    <button class="btn btn-approve" onclick="window.__browserUseApproval('{request_id}', 'approve')">
                        ✓ Approve
                    </button>
                    <button class="btn btn-deny" onclick="window.__browserUseApproval('{request_id}', 'deny')">
                        ✕ Deny
                    </button>
                </div>
                <div class="btn-row">
                    <button class="btn btn-secondary" onclick="window.__browserUseApproval('{request_id}', 'approve_session')">
                        Approve All (Session)
                    </button>
                    <button class="btn btn-secondary" onclick="window.__browserUseApproval('{request_id}', 'approve_domain')">
                        Approve All (Domain)
                    </button>
                </div>
                <div class="timer" id="approval-timer">Auto-deny in <span id="countdown">60</span>s</div>
            </div>
        </div>
    `;
    document.body.appendChild(popup);

    // Countdown timer
    let countdown = 60;
    const countdownEl = document.getElementById('countdown');
    const timer = setInterval(() => {{
        countdown--;
        if (countdownEl) countdownEl.textContent = countdown;
        if (countdown <= 0) {{
            clearInterval(timer);
            window.__browserUseApproval('{request_id}', 'timeout');
        }}
    }}, 1000);

    // Store timer reference for cleanup
    window.__browserUseApprovalTimer = timer;
}})();
"""

		# Track the approval tab for cleanup
		approval_tab_id = None
		# Save the original focus target to restore after approval
		original_focus_target_id = self.browser_session.agent_focus_target_id

		# Get the CDP session
		try:
			cdp_session = await self.browser_session.get_or_create_cdp_session()
			session_id = cdp_session.session_id

			# Always create a NEW TAB for the approval UI
			# This keeps the original page intact and provides a clean approval experience
			try:
				# Create a new tab using Target.createTarget
				result = await cdp_session.cdp_client.send.Target.createTarget(
					params={'url': 'about:blank'},
					session_id=session_id,
				)
				approval_tab_id = result.get('targetId')
				self.logger.debug(f'Created approval tab: {approval_tab_id}')

				# Get a CDP session for the new tab WITHOUT changing agent focus
				# We use focus=False to avoid disrupting the main session
				approval_session = await self.browser_session.get_or_create_cdp_session(approval_tab_id, focus=False)
				approval_session_id = approval_session.session_id

				# Activate the approval tab visually so user can see it
				await cdp_session.cdp_client.send.Target.activateTarget(
					params={'targetId': approval_tab_id},
					session_id=session_id,
				)
			except Exception as e:
				self.logger.warning(f'Failed to create approval tab: {e}, falling back to current page')
				approval_session = cdp_session
				approval_session_id = session_id

			# Create a full HTML page for the approval dialog
			full_page_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Browser Use - Permission Required</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .container {{
            background: #ffffff;
            border-radius: 16px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            max-width: 500px;
            width: 100%;
            overflow: hidden;
        }}
        .header {{
            background: {risk_color};
            color: white;
            padding: 24px;
            text-align: center;
        }}
        .header-icon {{
            font-size: 48px;
            margin-bottom: 12px;
        }}
        .header h1 {{
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 4px;
        }}
        .header p {{
            opacity: 0.9;
            font-size: 14px;
        }}
        .content {{
            padding: 24px;
        }}
        .step-progress {{
            background: #e0e7ff;
            color: #3730a3;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            display: inline-block;
            margin-bottom: 16px;
        }}
        .context-section {{
            background: #f8fafc;
            border-left: 3px solid #3b82f6;
            padding: 12px 16px;
            margin-bottom: 12px;
            border-radius: 0 8px 8px 0;
        }}
        .context-label {{
            font-size: 11px;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
            font-weight: 600;
        }}
        .context-value {{
            font-size: 14px;
            color: #1e293b;
            line-height: 1.5;
        }}
        .goal-value {{
            color: #059669;
            font-weight: 500;
        }}
        .reasoning-value {{
            color: #7c3aed;
            font-style: italic;
        }}
        .actions-section {{
            background: #fef3c7;
            border: 1px solid #fcd34d;
            border-radius: 8px;
            padding: 12px 16px;
            margin-bottom: 16px;
        }}
        .section-title {{
            font-size: 12px;
            color: #92400e;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
            font-weight: 600;
        }}
        .actions-list {{
            margin: 0;
            padding-left: 20px;
            font-size: 13px;
            color: #78350f;
        }}
        .actions-list li {{
            margin-bottom: 4px;
        }}
        .action-type {{
            background: #f3f4f6;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
        }}
        .action-type-label {{
            font-size: 12px;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }}
        .action-type-value {{
            font-size: 18px;
            font-weight: 600;
            color: #1f2937;
        }}
        .details {{
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 20px;
        }}
        .detail-row {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #e5e7eb;
        }}
        .detail-row:last-child {{
            border-bottom: none;
        }}
        .detail-key {{
            color: #6b7280;
            font-size: 14px;
        }}
        .detail-value {{
            color: #1f2937;
            font-size: 14px;
            font-weight: 500;
            word-break: break-all;
            max-width: 280px;
            text-align: right;
        }}
        .buttons {{
            display: grid;
            gap: 12px;
        }}
        .btn {{
            padding: 14px 20px;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .btn-approve {{
            background: #22c55e;
            color: white;
        }}
        .btn-approve:hover {{
            background: #16a34a;
        }}
        .btn-deny {{
            background: #ef4444;
            color: white;
        }}
        .btn-deny:hover {{
            background: #dc2626;
        }}
        .btn-secondary {{
            background: #e5e7eb;
            color: #374151;
        }}
        .btn-secondary:hover {{
            background: #d1d5db;
        }}
        .timer {{
            text-align: center;
            margin-top: 16px;
            color: #6b7280;
            font-size: 14px;
        }}
        .timer span {{
            font-weight: 600;
            color: #ef4444;
        }}
        .footer {{
            background: #f9fafb;
            padding: 16px 24px;
            text-align: center;
            font-size: 12px;
            color: #9ca3af;
            border-top: 1px solid #e5e7eb;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-icon">{risk_icon}</div>
            <h1>Permission Required</h1>
            <p>Browser Use Agent is requesting access</p>
        </div>
        <div class="content">
            {context_html}
            <div class="action-type">
                <div class="action-type-label">Action Type</div>
                <div class="action-type-value">{request.action_type.value.replace('_', ' ')}</div>
            </div>
            <div class="details">
                {details_html if details_html else '<div class="detail-row"><span class="detail-key">No additional details</span></div>'}
            </div>
            {actions_html}
            <div class="buttons">
                <button class="btn btn-approve" onclick="window.__browserUseApproval('{request_id}', 'approve')">
                    ✓ Allow This Action
                </button>
                <button class="btn btn-secondary" onclick="window.__browserUseApproval('{request_id}', 'approve_session')">
                    Allow All (This Session)
                </button>
                <button class="btn btn-secondary" onclick="window.__browserUseApproval('{request_id}', 'approve_domain')">
                    Allow All (This Domain)
                </button>
                <button class="btn btn-deny" onclick="window.__browserUseApproval('{request_id}', 'deny')">
                    ✕ Deny
                </button>
            </div>
            <div class="timer">
                Auto-deny in <span id="countdown">60</span> seconds
            </div>
        </div>
        <div class="footer">
            🔒 Browser Use Security Watchdog
        </div>
    </div>
    <script>
        window.__browserUseApprovalResult_{request_id} = null;
        window.__browserUseApproval = function(reqId, decision) {{
            if (reqId === '{request_id}') {{
                window.__browserUseApprovalResult_{request_id} = decision;
            }}
        }};
        
        let countdown = 60;
        const timer = setInterval(function() {{
            countdown--;
            document.getElementById('countdown').textContent = countdown;
            if (countdown <= 0) {{
                clearInterval(timer);
                window.__browserUseApproval('{request_id}', 'deny');
            }}
        }}, 1000);
    </script>
</body>
</html>"""

			# Get the frame tree to find the frame ID for the approval tab
			frame_tree = await approval_session.cdp_client.send.Page.getFrameTree(session_id=approval_session_id)
			frame_id = frame_tree['frameTree']['frame']['id']

			# Set the document content in the approval tab
			await approval_session.cdp_client.send.Page.setDocumentContent(
				params={'frameId': frame_id, 'html': full_page_html},
				session_id=approval_session_id,
			)

			# Poll for the result
			timeout = 65  # seconds (slightly more than countdown)
			poll_interval = 0.5
			elapsed = 0

			while elapsed < timeout:
				await asyncio.sleep(poll_interval)
				elapsed += poll_interval

				# Check for result in the approval tab
				check_result_js = f'window.__browserUseApprovalResult_{request_id}'
				result = await approval_session.cdp_client.send.Runtime.evaluate(
					params={'expression': check_result_js, 'returnByValue': True},
					session_id=approval_session_id,
				)

				if result and 'result' in result and result['result'].get('value'):
					decision_str = result['result']['value']

					# Close the approval tab and restore focus to original tab
					if approval_tab_id:
						try:
							await cdp_session.cdp_client.send.Target.closeTarget(
								params={'targetId': approval_tab_id},
								session_id=session_id,
							)
							self.logger.debug(f'Closed approval tab: {approval_tab_id}')
						except Exception as e:
							self.logger.debug(f'Failed to close approval tab: {e}')

						# Restore focus to the original tab
						if original_focus_target_id:
							try:
								await cdp_session.cdp_client.send.Target.activateTarget(
									params={'targetId': original_focus_target_id},
									session_id=session_id,
								)
								self.logger.debug(f'Restored focus to original tab: {original_focus_target_id}')
							except Exception as e:
								self.logger.debug(f'Failed to restore focus to original tab: {e}')

					# Map decision string to enum
					if decision_str == 'approve':
						return ApprovalDecision.APPROVE
					elif decision_str == 'approve_session':
						return ApprovalDecision.APPROVE_ALL_SESSION
					elif decision_str == 'approve_domain':
						return ApprovalDecision.APPROVE_ALL_DOMAIN
					else:
						return ApprovalDecision.DENY

			# Timeout - close approval tab and deny
			if approval_tab_id:
				try:
					await cdp_session.cdp_client.send.Target.closeTarget(
						params={'targetId': approval_tab_id},
						session_id=session_id,
					)
					# Restore focus to the original tab
					if original_focus_target_id:
						await cdp_session.cdp_client.send.Target.activateTarget(
							params={'targetId': original_focus_target_id},
							session_id=session_id,
						)
						self.logger.debug(f'Restored focus to original tab after timeout: {original_focus_target_id}')
				except Exception:
					pass
			self.logger.warning('⏱️ Browser UI approval timed out, denying action')
			return ApprovalDecision.DENY

		except Exception as e:
			# Close approval tab on error
			if approval_tab_id:
				try:
					cdp_session = await self.browser_session.get_or_create_cdp_session()
					await cdp_session.cdp_client.send.Target.closeTarget(
						params={'targetId': approval_tab_id},
						session_id=cdp_session.session_id,
					)
					# Restore focus to the original tab
					if original_focus_target_id:
						await cdp_session.cdp_client.send.Target.activateTarget(
							params={'targetId': original_focus_target_id},
							session_id=cdp_session.session_id,
						)
						self.logger.debug(f'Restored focus to original tab after error: {original_focus_target_id}')
				except Exception:
					pass
			self.logger.error(f'Failed to show browser UI approval popup: {e}')
			# Fallback to console prompt
			self.logger.info('Falling back to console approval prompt')
			return await self._console_approval_prompt(request)

	async def check_navigation_approval(self, event: NavigateToUrlEvent) -> None:
		"""Check if navigation requires approval. Called directly by BrowserSession, not via event bus.

		This method is intentionally NOT named on_NavigateToUrlEvent to avoid auto-registration
		as an event handler. We call it directly from BrowserSession.on_NavigateToUrlEvent to
		ensure approval happens BEFORE navigation, not concurrently via the event bus.

		Raises:
			PermissionDeniedError: If user denies the navigation (with context for re-planning)
			ValueError: If domain is in denied list (no re-planning possible)
		"""
		if not self.require_approval_for_navigation:
			return

		url = event.url
		domain = self._get_domain_from_url(url)

		# Skip internal URLs
		if url in ['about:blank', 'chrome://new-tab-page/', 'chrome://newtab/']:
			return

		# Check denied domains first
		if self._is_domain_denied(domain):
			self.logger.warning(f'⛔ Navigation to denied domain blocked: {url}')
			raise ValueError(f'Navigation to {url} blocked: domain is in denied list')

		# Check pre-approved domains
		if self._is_domain_approved(domain):
			self.logger.debug(f'✅ Navigation to pre-approved domain: {domain}')
			return

		# Determine risk level
		risk_level = 'high' if self._is_high_risk_domain(domain) else 'medium'

		# Create request with agent context
		request = ApprovalRequest(
			action_type=SensitiveActionType.NAVIGATION,
			description=f'Navigate to {url}',
			details={'url': url, 'domain': domain, 'new_tab': event.new_tab},
			risk_level=risk_level,
			url=url,
		)

		decision = await self._request_approval(request)
		if decision == ApprovalDecision.DENY:
			self.logger.warning(f'⛔ Navigation denied by user: {url}')

			# Get re-plan count for this goal
			goal_key = self._current_goal or url
			replan_count = self.get_replan_count(goal_key)

			# Raise PermissionDeniedError with context for smart handling
			raise PermissionDeniedError(
				message=f'Navigation to {url} denied by user',
				action_type=SensitiveActionType.NAVIGATION.value,
				url=url,
				current_goal=self._current_goal,
				reasoning=self._current_reasoning,
				is_critical=request.is_critical,
				replan_count=replan_count,
			)

		self.logger.info(f'✅ Navigation approved: {url}')

	async def on_TypeTextEvent(self, event: TypeTextEvent) -> None:
		"""Intercept text input events and request approval for sensitive fields."""
		element_node = event.node
		text = event.text

		# Detect sensitive field type
		field_type, risk_level = self._detect_sensitive_field_type(element_node)

		# Check if approval is needed
		needs_approval = False
		if self.require_approval_for_forms:
			needs_approval = True
		elif self.require_approval_for_sensitive_data and field_type:
			needs_approval = True
		elif event.is_sensitive:
			needs_approval = True
			risk_level = 'high'

		if not needs_approval:
			return

		# Get current URL
		try:
			url = await self.browser_session.get_current_page_url()
		except Exception:
			url = None

		# Mask sensitive text in the prompt
		display_text = text
		if field_type in ['password', 'credit_card', 'cvv', 'ssn', 'api_key'] or event.is_sensitive:
			display_text = '*' * min(len(text), 8) + '...' if len(text) > 8 else '*' * len(text)

		action_type = SensitiveActionType.SENSITIVE_DATA_INPUT if field_type else SensitiveActionType.FORM_INPUT

		request = ApprovalRequest(
			action_type=action_type,
			description=f'Enter {"sensitive " if field_type else ""}text into form field',
			details={
				'field_type': field_type or 'text',
				'text_preview': display_text,
				'text_length': len(text),
				'is_sensitive': event.is_sensitive,
			},
			risk_level=risk_level,
			url=url,
			element_info=self._get_element_info(element_node),
		)

		decision = await self._request_approval(request)
		if decision == ApprovalDecision.DENY:
			self.logger.warning('⛔ Text input denied by user')
			raise ValueError('Text input denied by user')

		self.logger.info(f'✅ Text input approved for {field_type or "text"} field')

	async def on_ClickElementEvent(self, event: ClickElementEvent) -> None:
		"""Intercept click events and request approval for sensitive buttons."""
		element_node = event.node

		# Detect sensitive button type
		button_type, risk_level = self._detect_sensitive_button_type(element_node)

		if not button_type:
			return  # Not a sensitive button

		# Get current URL
		try:
			url = await self.browser_session.get_current_page_url()
		except Exception:
			url = None

		# Increase risk for high-risk domains
		if self._is_high_risk_domain(self._get_domain_from_url(url) if url else None):
			risk_level = 'critical' if risk_level == 'high' else 'high'

		action_type_map = {
			'submit': SensitiveActionType.CLICK_SUBMIT,
			'login': SensitiveActionType.CLICK_LOGIN,
			'payment': SensitiveActionType.CLICK_PAYMENT,
			'delete': SensitiveActionType.CLICK_SUBMIT,
			'transfer': SensitiveActionType.CLICK_PAYMENT,
		}
		action_type = action_type_map.get(button_type, SensitiveActionType.CLICK_SUBMIT)

		request = ApprovalRequest(
			action_type=action_type,
			description=f'Click {button_type} button',
			details={'button_type': button_type},
			risk_level=risk_level,
			url=url,
			element_info=self._get_element_info(element_node),
		)

		decision = await self._request_approval(request)
		if decision == ApprovalDecision.DENY:
			self.logger.warning(f'⛔ Click on {button_type} button denied by user')
			raise ValueError(f'Click on {button_type} button denied by user')

		self.logger.info(f'✅ Click on {button_type} button approved')

	async def on_UploadFileEvent(self, event: UploadFileEvent) -> None:
		"""Intercept file upload events and request approval."""
		if not self.require_approval_for_file_operations:
			return

		file_path = event.file_path

		# Get current URL
		try:
			url = await self.browser_session.get_current_page_url()
		except Exception:
			url = None

		request = ApprovalRequest(
			action_type=SensitiveActionType.FILE_UPLOAD,
			description=f'Upload file: {file_path}',
			details={'file_path': file_path},
			risk_level='high',
			url=url,
			element_info=self._get_element_info(event.node),
		)

		decision = await self._request_approval(request)
		if decision == ApprovalDecision.DENY:
			self.logger.warning(f'⛔ File upload denied by user: {file_path}')
			raise ValueError(f'File upload denied by user: {file_path}')

		self.logger.info(f'✅ File upload approved: {file_path}')

	async def on_SendKeysEvent(self, event: SendKeysEvent) -> None:
		"""Intercept keyboard shortcut events that could be dangerous."""
		keys = event.keys.lower()

		# Detect potentially dangerous keyboard shortcuts
		dangerous_shortcuts = [
			('ctrl+shift+delete', 'Clear browsing data'),
			('cmd+shift+delete', 'Clear browsing data'),
			('ctrl+w', 'Close tab'),
			('cmd+w', 'Close tab'),
			('ctrl+shift+n', 'Open incognito'),
			('cmd+shift+n', 'Open incognito'),
			('alt+f4', 'Close window'),
			('cmd+q', 'Quit application'),
		]

		for shortcut, description in dangerous_shortcuts:
			if shortcut in keys:
				try:
					url = await self.browser_session.get_current_page_url()
				except Exception:
					url = None

				request = ApprovalRequest(
					action_type=SensitiveActionType.KEYBOARD_SHORTCUT,
					description=f'Execute keyboard shortcut: {keys} ({description})',
					details={'keys': keys, 'action': description},
					risk_level='medium',
					url=url,
				)

				decision = await self._request_approval(request)
				if decision == ApprovalDecision.DENY:
					self.logger.warning(f'⛔ Keyboard shortcut denied by user: {keys}')
					raise ValueError(f'Keyboard shortcut denied by user: {keys}')

				self.logger.info(f'✅ Keyboard shortcut approved: {keys}')
				return

	async def on_FileDownloadedEvent(self, event: FileDownloadedEvent) -> None:
		"""Log file downloads for audit purposes (post-action notification)."""
		self.logger.info(f'📥 File downloaded: {event.file_name} ({event.file_size} bytes) from {event.url} to {event.path}')
