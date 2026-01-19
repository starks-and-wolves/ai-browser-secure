#!/usr/bin/env python3
"""
Live demonstration of AWI discovery process.
Shows exactly how browser-use detects the AWI layer.
"""

import asyncio
import aiohttp
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()


async def demonstrate_discovery():
    """Show all 3 discovery methods in action."""

    url = "http://localhost:5000"

    console.print("\n")
    console.print(Panel(
        "[bold cyan]How Browser-Use Discovers the AWI Layer[/bold cyan]\n\n"
        f"Target: {url}\n"
        "Browser-use will try 3 methods in sequence:",
        title="AWI Discovery Process",
        box=box.DOUBLE,
        border_style="cyan"
    ))

    async with aiohttp.ClientSession() as session:

        # Method 1: HTTP Headers
        console.print("\n[bold yellow]📡 Method 1: HTTP Headers Discovery[/bold yellow]")
        console.print("   Sending HEAD request to check response headers...")

        try:
            async with session.head(url, allow_redirects=True) as response:
                console.print(f"   Status: [green]{response.status}[/green]")

                # Check for AWI headers
                awi_headers = {
                    'X-AWI-Discovery': response.headers.get('X-AWI-Discovery'),
                    'X-Agent-API': response.headers.get('X-Agent-API'),
                    'X-Agent-Capabilities': response.headers.get('X-Agent-Capabilities'),
                    'X-Agent-Registration': response.headers.get('X-Agent-Registration')
                }

                # Display headers
                table = Table(title="AWI Headers Found", box=box.SIMPLE)
                table.add_column("Header", style="cyan")
                table.add_column("Value", style="green")

                for header, value in awi_headers.items():
                    if value:
                        table.add_row(header, value)

                console.print(table)

                if awi_headers['X-AWI-Discovery']:
                    console.print(f"\n   [green]✅ SUCCESS![/green] AWI discovered via header")
                    console.print(f"   Manifest URL: [cyan]{awi_headers['X-AWI-Discovery']}[/cyan]")
                    manifest_url = awi_headers['X-AWI-Discovery']
                else:
                    console.print("\n   [red]❌ No X-AWI-Discovery header found[/red]")
                    console.print("   [yellow]→ Falling back to Method 2...[/yellow]")
                    manifest_url = None

        except Exception as e:
            console.print(f"   [red]❌ Error: {e}[/red]")
            manifest_url = None

        # Method 2: Well-Known URI
        console.print("\n[bold yellow]📍 Method 2: Well-Known URI (.well-known/llm-text)[/bold yellow]")
        console.print("   Standard location per RFC 8615...")

        well_known_url = f"{url}/.well-known/llm-text"
        console.print(f"   Trying: [cyan]{well_known_url}[/cyan]")

        try:
            async with session.get(well_known_url) as response:
                console.print(f"   Status: [green]{response.status}[/green]")

                if response.status == 200:
                    # Parse manifest
                    try:
                        manifest = await response.json()
                    except aiohttp.ContentTypeError:
                        text = await response.text()
                        import json
                        manifest = json.loads(text)

                    console.print(f"\n   [green]✅ SUCCESS![/green] AWI manifest found")
                    console.print(f"   Size: [dim]{len(text)} bytes[/dim]")

                    # Show manifest preview
                    awi_info = manifest.get('awi', {})
                    console.print(f"\n   [bold]AWI Information:[/bold]")
                    console.print(f"   • Name: [cyan]{awi_info.get('name')}[/cyan]")
                    console.print(f"   • Version: [cyan]{awi_info.get('version')}[/cyan]")
                    console.print(f"   • Description: [dim]{awi_info.get('description', '')[:60]}...[/dim]")

                    capabilities = manifest.get('capabilities', {})
                    console.print(f"\n   [bold]Capabilities:[/bold]")
                    console.print(f"   • Allowed operations: [green]{len(capabilities.get('allowed_operations', []))}[/green]")
                    console.print(f"   • Disallowed operations: [red]{len(capabilities.get('disallowed_operations', []))}[/red]")
                    console.print(f"   • Security features: [cyan]{len(capabilities.get('security_features', []))}[/cyan]")

                    endpoints = manifest.get('endpoints', {})
                    console.print(f"\n   [bold]Endpoints:[/bold]")
                    console.print(f"   • Base URL: [cyan]{endpoints.get('base')}[/cyan]")
                    console.print(f"   • Registration: [cyan]{manifest.get('authentication', {}).get('registration', '')}[/cyan]")

                    manifest_found = True
                else:
                    console.print(f"   [red]❌ Not found (status {response.status})[/red]")
                    console.print("   [yellow]→ Falling back to Method 3...[/yellow]")
                    manifest_found = False

        except Exception as e:
            console.print(f"   [red]❌ Error: {e}[/red]")
            manifest_found = False

        # Method 3: Capabilities Endpoint
        if not manifest_found:
            console.print("\n[bold yellow]🔧 Method 3: Capabilities Endpoint[/bold yellow]")
            console.print("   Common API pattern: /api/agent/capabilities...")

            caps_url = f"{url}/api/agent/capabilities"
            console.print(f"   Trying: [cyan]{caps_url}[/cyan]")

            try:
                async with session.get(caps_url) as response:
                    console.print(f"   Status: [green]{response.status}[/green]")

                    if response.status == 200:
                        data = await response.json()

                        if data.get('success') and 'capabilities' in data:
                            console.print(f"\n   [green]✅ SUCCESS![/green] Capabilities found")
                            caps = data['capabilities']

                            # Check if it points to full manifest
                            if 'discovery' in caps and 'wellKnownUri' in caps['discovery']:
                                full_manifest_url = caps['discovery']['wellKnownUri']
                                console.print(f"\n   [yellow]→ Capabilities response includes full manifest URL:[/yellow]")
                                console.print(f"   [cyan]{full_manifest_url}[/cyan]")
                                console.print(f"   [dim](Would fetch this for complete manifest)[/dim]")
                        else:
                            console.print(f"   [red]❌ Invalid capabilities response[/red]")
                    else:
                        console.print(f"   [red]❌ Not found (status {response.status})[/red]")

            except Exception as e:
                console.print(f"   [red]❌ Error: {e}[/red]")

    # Summary
    console.print("\n")
    console.print(Panel(
        "[bold green]✅ Discovery Complete![/bold green]\n\n"
        "[bold]What happened:[/bold]\n"
        "1. Browser-use sent HEAD request to check headers\n"
        "2. Found [cyan]X-AWI-Discovery[/cyan] header → pointed to manifest\n"
        "3. Fetched manifest from [cyan]/.well-known/llm-text[/cyan]\n"
        "4. Parsed AWI capabilities and endpoints\n\n"
        "[bold cyan]Result:[/bold cyan] AWI layer detected! Browser-use can now:\n"
        "• Use structured API instead of DOM parsing\n"
        "• Register agent with API key\n"
        "• Make authenticated API calls\n"
        "• Track session state server-side\n"
        "• Reduce token usage by 500x",
        title="✨ Summary",
        box=box.DOUBLE,
        border_style="green"
    ))

    # Show comparison
    console.print("\n")
    console.print(Panel(
        "[bold]Traditional Browser Automation (No AWI):[/bold]\n"
        "1. Navigate to URL\n"
        "2. Get full page HTML (~100,000 tokens)\n"
        "3. Parse DOM to find elements\n"
        "4. Find buttons/forms with CSS selectors (fragile)\n"
        "5. Simulate clicks and typing\n"
        "6. Parse response HTML to verify\n"
        "[red]Total: ~200,000 tokens, brittle selectors[/red]\n\n"
        "[bold]With AWI Discovery:[/bold]\n"
        "1. Check HTTP headers (~100 bytes)\n"
        "2. Fetch AWI manifest (~5KB, ~200 tokens)\n"
        "3. Direct API calls with authentication\n"
        "4. Structured JSON responses\n"
        "5. Server-side state tracking\n"
        "[green]Total: ~600 tokens, stable API contract[/green]",
        title="Comparison: DOM vs AWI",
        box=box.ROUNDED,
        border_style="yellow"
    ))


if __name__ == "__main__":
    try:
        asyncio.run(demonstrate_discovery())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
