#!/usr/bin/env python3
"""
Demo Simulator for MCP DM Motivator
This script simulates 4 different scenarios:
1. Messi scoring a goal
2. Ronaldo scoring a goal  
3. Manchester United winning a match
4. Manchester City winning a match

Each scenario will trigger a DM to the rival fan page.
"""

import time
import sys
import os
from rivals import RIVALRIES, get_fan_to_notify, get_rival_name, get_supported_entity, is_player, is_team
from goal_scraper import generate_banter_message
import dm_sender

def simulate_scenario(entity_id, entity_name, entity_type, scenario_description):
    """Simulate a single scenario (goal or win)"""
    print(f"\n{'='*60}")
    print(f"🎬 DEMO SCENARIO: {scenario_description}")
    print(f"{'='*60}")
    
    # Get the fan to notify
    fan_to_notify = get_fan_to_notify(entity_id)
    if not fan_to_notify:
        print(f"❌ No fan configured for {entity_name}")
        return
    
    print(f"📱 Target fan page: {fan_to_notify}")
    print(f"🎯 Entity: {entity_name} ({entity_type})")
    print(f"🏆 Supported entity: {get_supported_entity(entity_id)}")
    
    # Generate a simulated count (for demo purposes)
    simulated_count = 5 if entity_type == "player" else 3
    
    # Generate banter message
    print(f"💬 Generating banter message...")
    message = generate_banter_message(
        scorer_name=entity_name,
        supported_entity=get_supported_entity(entity_id),
        current_count=simulated_count,
        entity_type=entity_type
    )
    
    print(f"📝 Generated message:")
    print(f"   {message}")
    
    # Send the DM
    print(f"🚀 Sending DM to {fan_to_notify}...")
    try:
        dm_sender.send_rival_dm_sync(
            recipient_username=fan_to_notify,
            message=message
        )
        print(f"✅ Demo scenario completed successfully!")
    except Exception as e:
        print(f"❌ Error sending DM: {e}")
    
    print(f"⏳ Waiting 10 seconds before next scenario...")
    time.sleep(10)

def run_demo():
    """Run all 4 demo scenarios"""
    print("🎬 Starting MCP DM Motivator Demo")
    print("This demo will simulate 4 different scenarios:")
    print("1. Messi scoring a goal")
    print("2. Ronaldo scoring a goal")
    print("3. Manchester United winning a match")
    print("4. Manchester City winning a match")
    print("\nEach scenario will send a DM to the corresponding rival fan page.")
    
    # Wait for user confirmation
    input("\nPress Enter to start the demo...")
    
    scenarios = [
        {
            "id": "154",  # Messi
            "name": "Lionel Messi",
            "type": "player",
            "description": "Messi scores a goal! 🐐⚽"
        },
        {
            "id": "85",   # Ronaldo
            "name": "Cristiano Ronaldo", 
            "type": "player",
            "description": "Ronaldo scores a goal! 🚀⚽"
        },
        {
            "id": "33",   # Manchester United
            "name": "Manchester United",
            "type": "team", 
            "description": "Manchester United wins a match! 🔴⚽"
        },
        {
            "id": "50",   # Manchester City
            "name": "Manchester City",
            "type": "team",
            "description": "Manchester City wins a match! 💙⚽"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🎯 Running scenario {i}/4...")
        simulate_scenario(
            entity_id=scenario["id"],
            entity_name=scenario["name"],
            entity_type=scenario["type"],
            scenario_description=scenario["description"]
        )
    
    print(f"\n{'='*60}")
    print("🎉 Demo completed! All 4 scenarios have been executed.")
    print("Check the target Instagram accounts for the DMs.")
    print(f"{'='*60}")

if __name__ == "__main__":
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        sys.exit(1) 