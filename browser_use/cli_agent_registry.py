#!/usr/bin/env python3
"""
CLI tool for managing AWI agent credentials registry.

Usage:
    python -m browser_use.cli_agent_registry list
    python -m browser_use.cli_agent_registry show <agent_id>
    python -m browser_use.cli_agent_registry delete <agent_id>
    python -m browser_use.cli_agent_registry deactivate <agent_id>
    python -m browser_use.cli_agent_registry cleanup
"""

import sys
from datetime import datetime
from tabulate import tabulate

from browser_use.agent_registry import agent_registry


def format_timestamp(ts: str | None) -> str:
	"""Format ISO timestamp to human-readable format."""
	if not ts:
		return 'Never'
	try:
		dt = datetime.fromisoformat(ts)
		now = datetime.utcnow()
		diff = now - dt

		# Format relative time
		if diff.days > 0:
			return f'{diff.days}d ago'
		elif diff.seconds >= 3600:
			return f'{diff.seconds // 3600}h ago'
		elif diff.seconds >= 60:
			return f'{diff.seconds // 60}m ago'
		else:
			return 'Just now'
	except Exception:
		return ts[:19]  # Return ISO format truncated


def list_agents(domain: str | None = None, show_inactive: bool = False):
	"""List all registered agents."""
	credentials = agent_registry.list_credentials(
		domain=domain,
		active_only=not show_inactive
	)

	if not credentials:
		print('No agents found in registry.')
		return

	# Prepare table data
	table_data = []
	for cred in credentials:
		status = '✅' if cred.is_active and not cred.is_expired() else '❌'
		if cred.is_expired():
			status = '⏰ Expired'

		table_data.append([
			cred.agent_id[:12] + '...',
			cred.agent_name,
			cred.domain,
			', '.join(cred.permissions),
			format_timestamp(cred.last_used),
			cred.session_count,
			status,
		])

	headers = ['Agent ID', 'Name', 'Domain', 'Permissions', 'Last Used', 'Sessions', 'Status']
	print('\n📋 Registered AWI Agents:')
	print(tabulate(table_data, headers=headers, tablefmt='grid'))
	print(f'\nTotal: {len(credentials)} agent(s)')


def show_agent(agent_id: str):
	"""Show detailed information about an agent."""
	cred = agent_registry.get_credentials_by_id(agent_id)

	if not cred:
		print(f'❌ Agent {agent_id} not found')
		return

	print('\n' + '=' * 70)
	print(f'Agent Details: {cred.agent_name}')
	print('=' * 70)
	print(f'Agent ID:        {cred.agent_id}')
	print(f'Agent Name:      {cred.agent_name}')
	print(f'Domain:          {cred.domain}')
	print(f'AWI Name:        {cred.awi_name}')
	print(f'Agent Type:      {cred.agent_type}')
	print(f'Framework:       {cred.framework}')
	print(f'')
	print(f'Permissions:     {", ".join(cred.permissions)}')
	print(f'API Key:         {cred.api_key[:20]}...{cred.api_key[-10:]}')
	print(f'')
	print(f'Created:         {cred.created_at}')
	print(f'Last Used:       {cred.last_used or "Never"}')
	print(f'Session Count:   {cred.session_count}')
	print(f'')
	print(f'Active:          {"✅ Yes" if cred.is_active else "❌ No"}')
	print(f'Expired:         {"⏰ Yes" if cred.is_expired() else "✅ No"}')

	if cred.expires_at:
		print(f'Expires At:      {cred.expires_at}')

	if cred.description:
		print(f'')
		print(f'Description:     {cred.description}')

	if cred.notes:
		print(f'Notes:           {cred.notes}')

	if cred.manifest_version:
		print(f'Manifest Ver:    {cred.manifest_version}')

	print('=' * 70 + '\n')


def delete_agent(agent_id: str, confirm: bool = False):
	"""Delete an agent from the registry."""
	cred = agent_registry.get_credentials_by_id(agent_id)

	if not cred:
		print(f'❌ Agent {agent_id} not found')
		return

	if not confirm:
		print(f'\n⚠️  About to delete agent:')
		print(f'   Agent ID:   {cred.agent_id}')
		print(f'   Name:       {cred.agent_name}')
		print(f'   Domain:     {cred.domain}')
		print(f'')
		response = input('Are you sure? (yes/no): ')
		if response.lower() != 'yes':
			print('❌ Cancelled')
			return

	if agent_registry.delete_credentials(agent_id):
		print(f'✅ Agent {cred.agent_name} deleted successfully')
	else:
		print(f'❌ Failed to delete agent')


def deactivate_agent(agent_id: str):
	"""Deactivate an agent (mark as inactive)."""
	cred = agent_registry.get_credentials_by_id(agent_id)

	if not cred:
		print(f'❌ Agent {agent_id} not found')
		return

	if agent_registry.deactivate_credentials(agent_id):
		print(f'✅ Agent {cred.agent_name} deactivated')
		print(f'   (Credentials preserved but will not be used)')
	else:
		print(f'❌ Failed to deactivate agent')


def cleanup_expired():
	"""Remove expired credentials."""
	count = agent_registry.cleanup_expired()
	if count > 0:
		print(f'✅ Removed {count} expired credential(s)')
	else:
		print('✅ No expired credentials found')


def main():
	"""Main CLI entry point."""
	if len(sys.argv) < 2:
		print(__doc__)
		sys.exit(1)

	command = sys.argv[1]

	try:
		if command == 'list':
			domain = sys.argv[2] if len(sys.argv) > 2 else None
			show_inactive = '--all' in sys.argv
			list_agents(domain, show_inactive)

		elif command == 'show':
			if len(sys.argv) < 3:
				print('Usage: show <agent_id>')
				sys.exit(1)
			show_agent(sys.argv[2])

		elif command == 'delete':
			if len(sys.argv) < 3:
				print('Usage: delete <agent_id>')
				sys.exit(1)
			delete_agent(sys.argv[2], '--yes' in sys.argv)

		elif command == 'deactivate':
			if len(sys.argv) < 3:
				print('Usage: deactivate <agent_id>')
				sys.exit(1)
			deactivate_agent(sys.argv[2])

		elif command == 'cleanup':
			cleanup_expired()

		elif command in ['help', '-h', '--help']:
			print(__doc__)

		else:
			print(f'Unknown command: {command}')
			print(__doc__)
			sys.exit(1)

	except KeyboardInterrupt:
		print('\n\n⚠️  Cancelled by user')
		sys.exit(1)
	except Exception as e:
		print(f'\n❌ Error: {e}')
		import traceback
		traceback.print_exc()
		sys.exit(1)


if __name__ == '__main__':
	main()
