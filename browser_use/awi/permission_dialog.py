"""
AWI Permission Dialog

Displays a user prompt before agent registration to:
1. Show available permissions from AWI manifest
2. Let user select which permissions to grant
3. Show security features and rate limits
4. Get user confirmation before proceeding
"""

import logging
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Confirm, Prompt
from rich import box

logger = logging.getLogger(__name__)
console = Console()


class AWIPermissionDialog:
    """Interactive permission dialog for AWI agent registration."""

    def __init__(self, manifest: Dict[str, Any]):
        """
        Initialize permission dialog with AWI manifest.

        Args:
            manifest: Complete AWI manifest from discovery
        """
        self.manifest = manifest
        self.awi_info = manifest.get('awi', {})
        self.auth_info = manifest.get('authentication', {})
        self.capabilities = manifest.get('capabilities', {})

    def show_and_get_permissions(self) -> Optional[Dict[str, Any]]:
        """
        Display AWI information and get user approval for permissions.

        Returns:
            Dictionary with:
            - approved: bool - Whether user approved
            - permissions: List[str] - Selected permissions
            - agent_name: str - Name for the agent
            Or None if user declined
        """
        console.print("\n")
        console.rule("[bold blue]🤖 AWI Mode - Agent Registration Required[/bold blue]")
        console.print()

        # Show AWI information
        self._display_awi_info()

        # Show security features
        self._display_security_features()

        # Show available operations
        self._display_operations()

        # Show rate limits
        self._display_rate_limits()

        # Ask for user confirmation
        console.print()
        if not Confirm.ask(
            "[bold yellow]❓ Do you want to register an agent with this AWI?[/bold yellow]",
            default=False
        ):
            console.print("[red]❌ User declined AWI registration[/red]")
            return None

        # Get agent name
        default_name = "BrowserUseAgent"
        agent_name = Prompt.ask(
            "[bold cyan]🏷️  Agent name[/bold cyan]",
            default=default_name
        )

        # Get permission selection
        selected_permissions = self._select_permissions()

        if not selected_permissions:
            console.print("[red]❌ No permissions selected[/red]")
            return None

        # Show summary and final confirmation
        if not self._confirm_registration(agent_name, selected_permissions):
            console.print("[red]❌ Registration cancelled[/red]")
            return None

        console.print("[green]✅ Registration approved![/green]")
        return {
            'approved': True,
            'permissions': selected_permissions,
            'agent_name': agent_name
        }

    def _display_awi_info(self):
        """Display basic AWI information."""
        table = Table(
            title="🌐 AWI Information",
            box=box.ROUNDED,
            show_header=False,
            title_style="bold blue"
        )
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Name", self.awi_info.get('name', 'Unknown'))
        table.add_row("Description", self.awi_info.get('description', 'N/A'))
        table.add_row("Version", self.awi_info.get('version', 'Unknown'))
        table.add_row("Specification", self.awi_info.get('specification', 'Unknown'))
        table.add_row("Provider", self.awi_info.get('provider', 'Unknown'))

        console.print(table)
        console.print()

    def _display_security_features(self):
        """Display security features and policies."""
        security_features = self.capabilities.get('security_features', [])

        if not security_features:
            return

        table = Table(
            title="🔒 Security Features",
            box=box.ROUNDED,
            show_header=True,
            title_style="bold yellow"
        )
        table.add_column("Feature", style="cyan")
        table.add_column("Status", style="green")

        for feature in security_features:
            if ':' in feature:
                name, value = feature.split(':', 1)
                table.add_row(name.strip(), value.strip())
            else:
                table.add_row(feature, "enabled")

        console.print(table)
        console.print()

    def _display_operations(self):
        """Display allowed and disallowed operations."""
        allowed = self.capabilities.get('allowed_operations', [])
        disallowed = self.capabilities.get('disallowed_operations', [])

        table = Table(
            title="⚙️  Operations",
            box=box.ROUNDED,
            show_header=True,
            title_style="bold green"
        )
        table.add_column("Allowed ✅", style="green")
        table.add_column("Disallowed 🚫", style="red")

        # Pad lists to same length
        max_len = max(len(allowed), len(disallowed))
        allowed_padded = allowed + [''] * (max_len - len(allowed))
        disallowed_padded = disallowed + [''] * (max_len - len(disallowed))

        for allow, disallow in zip(allowed_padded, disallowed_padded):
            table.add_row(allow, disallow)

        console.print(table)
        console.print()

    def _display_rate_limits(self):
        """Display rate limits (if configured)."""
        rate_limits = self.capabilities.get('rate_limits', {})

        if not rate_limits or rate_limits.get('status') == 'not_implemented':
            console.print(Panel(
                "[yellow]⏱️  Rate limits: Not yet enforced (planned)[/yellow]",
                box=box.ROUNDED
            ))
            console.print()
            return

        planned = rate_limits.get('planned_limits', {})
        if planned:
            table = Table(
                title="⏱️  Rate Limits",
                box=box.ROUNDED,
                show_header=True,
                title_style="bold magenta"
            )
            table.add_column("Operation", style="cyan")
            table.add_column("Limit", style="yellow")

            for operation, limit in planned.items():
                table.add_row(operation.replace('_', ' ').title(), limit)

            console.print(table)
            console.print()

    def _select_permissions(self) -> List[str]:
        """
        Let user select which permissions to request.

        Returns:
            List of selected permission names
        """
        permissions_config = self.auth_info.get('permissions', {})
        available_perms = permissions_config.get('available', ['read', 'write', 'delete'])
        default_perms = permissions_config.get('default', ['read'])

        console.print(Panel(
            f"[bold cyan]🔑 Available Permissions:[/bold cyan]\n\n"
            f"• [green]read[/green] - View posts, comments, and content\n"
            f"• [yellow]write[/yellow] - Create posts and comments\n"
            f"• [red]delete[/red] - Delete content (if allowed)\n\n"
            f"[dim]Default: {', '.join(default_perms)}[/dim]",
            title="Permission Selection",
            box=box.DOUBLE
        ))

        console.print()
        console.print("[bold]Select permissions (comma-separated):[/bold]")
        console.print(f"Available: [cyan]{', '.join(available_perms)}[/cyan]")
        console.print(f"Default: [dim]{', '.join(default_perms)}[/dim]")

        selected = Prompt.ask(
            "\n[bold]Permissions[/bold]",
            default=','.join(default_perms)
        )

        # Parse comma-separated list
        permissions = [p.strip().lower() for p in selected.split(',') if p.strip()]

        # Validate permissions
        valid_permissions = [p for p in permissions if p in available_perms]

        if not valid_permissions:
            console.print(f"[red]⚠️  Invalid permissions. Using default: {', '.join(default_perms)}[/red]")
            return default_perms

        # Show disallowed operations based on permissions
        if 'delete' not in valid_permissions:
            console.print("[yellow]ℹ️  Note: Delete operations will be disabled[/yellow]")
        if 'write' not in valid_permissions:
            console.print("[yellow]ℹ️  Note: Write operations will be disabled[/yellow]")

        return valid_permissions

    def _confirm_registration(self, agent_name: str, permissions: List[str]) -> bool:
        """
        Show registration summary and get final confirmation.

        Args:
            agent_name: Name of the agent to register
            permissions: Selected permissions

        Returns:
            True if user confirms, False otherwise
        """
        console.print()
        console.print(Panel(
            f"[bold]Agent Name:[/bold] {agent_name}\n"
            f"[bold]Permissions:[/bold] {', '.join(permissions)}\n"
            f"[bold]AWI:[/bold] {self.awi_info.get('name', 'Unknown')}\n"
            f"[bold]Endpoint:[/bold] {self.auth_info.get('registration', 'Unknown')}",
            title="📋 Registration Summary",
            box=box.DOUBLE,
            border_style="green"
        ))

        console.print()
        return Confirm.ask(
            "[bold green]✅ Proceed with registration?[/bold green]",
            default=True
        )

    @staticmethod
    def show_registration_success(agent_info: Dict[str, Any]):
        """
        Display successful registration information.

        Args:
            agent_info: Agent registration response
        """
        console.print()
        console.print(Panel(
            f"[bold green]✅ Agent Registered Successfully![/bold green]\n\n"
            f"[bold]Agent ID:[/bold] {agent_info.get('id', 'N/A')}\n"
            f"[bold]API Key:[/bold] {agent_info.get('apiKey', 'N/A')[:30]}...\n"
            f"[bold]Permissions:[/bold] {', '.join(agent_info.get('permissions', []))}\n\n"
            f"[dim]The API key will be used for all subsequent requests.[/dim]",
            title="🎉 Registration Complete",
            box=box.DOUBLE,
            border_style="green"
        ))
        console.print()

    @staticmethod
    def show_awi_mode_banner():
        """Display AWI mode activation banner."""
        console.print()
        console.print(Panel(
            "[bold cyan]🚀 AWI Mode Activated[/bold cyan]\n\n"
            "Browser-use will interact with this website using a structured API\n"
            "instead of DOM parsing. This provides:\n\n"
            "• [green]500x token reduction[/green]\n"
            "• [green]Server-side session state[/green]\n"
            "• [green]Structured responses with metadata[/green]\n"
            "• [green]Trajectory tracking for debugging[/green]\n"
            "• [green]Explicit security policies[/green]",
            title="AWI Mode",
            box=box.DOUBLE,
            border_style="cyan"
        ))
        console.print()
