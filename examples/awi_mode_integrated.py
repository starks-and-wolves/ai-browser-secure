#!/usr/bin/env python3
"""
Browser-Use with AWI Mode - Integrated Example

This example demonstrates the newly integrated AWI mode in browser-use.
AWI mode enables the agent to use structured APIs instead of DOM parsing.

Features:
- Automatic AWI discovery
- Interactive user permission dialog
- Structured API communication
- 500x token reduction
- Session state tracking

Usage:
    python examples/awi_mode_integrated.py
"""

import asyncio
from browser_use import Agent, Browser
from langchain_openai import ChatOpenAI


async def main():
    """Example: Using browser-use with AWI mode enabled."""

    # Create agent with AWI mode enabled
    agent = Agent(
        task="Go to http://localhost:5000 and create a blog post about AI automation",
        llm=ChatOpenAI(model="gpt-4"),
        browser=Browser(headless=False),
        awi_mode=True,  # Enable AWI mode!
    )

    # Run the agent
    # If AWI is discovered:
    #   1. User will see permission dialog
    #   2. User approves or declines
    #   3. If approved: agent uses AWI API
    #   4. If declined: agent falls back to DOM
    # If no AWI found:
    #   - Agent automatically uses DOM parsing
    result = await agent.run(max_steps=20)

    # Check results
    if agent.awi_manager:
        print("\n✅ AWI Mode was active!")

        # Get session statistics
        state = await agent.get_awi_session_state()
        if state and state.get('success'):
            print(f"   Session ID: {state.get('sessionId')}")
            print(f"   Actions: {state['statistics'].get('totalActions')}")

        # Get action trajectory
        history = await agent.get_awi_action_history()
        if history and history.get('success'):
            print(f"   Trajectory: {len(history.get('trajectory', []))} steps")
    else:
        print("\n⚠️  Traditional DOM parsing was used")

    print(f"\n📝 Task completed: {result.is_done()}")
    return result


if __name__ == "__main__":
    asyncio.run(main())
