# rivals.py

"""
The Rivalry Engine
This file defines the rivalries and their target recipients.
- The key is the Player ID from the API-Football API.
- 'name' is the player's name for display.
- 'rival_name' is the name of their rival.
- 'fan_instagram_username' is who gets the DM when this player scores.
"""

# Rivalry configurations
RIVALRIES = [
    # Individual player rivalries
    {
        "id": "85",  # Ronaldo
        "name": "Cristiano Ronaldo",
        "type": "player",
        "rival_name": "Lionel Messi",
        "supported_player": "Lionel Messi",  # This is who we support/motivate for
        "target_username": "cr7ir"  # Ronaldo fan page - gets notified when Messi scores
    },
    {
        "id": "154",  # Messi  
        "name": "Lionel Messi",
        "type": "player", 
        "rival_name": "Cristiano Ronaldo",
        "supported_player": "Cristiano Ronaldo",  # This is who we support/motivate for
        "target_username": "we.are.messi"  # Messi fan page - gets notified when Ronaldo scores
    },
    
    # Team rivalries - tracking wins instead of goals
    {
        "id": "50",  # Manchester City (correct ID)
        "name": "Manchester City",
        "type": "team",
        "rival_name": "Manchester United", 
        "supported_team": "Manchester United",  # This is who we support/motivate for
        "target_username": "mancity_mcfc"  # Man City fan page - gets notified when Man United wins
    },
    {
        "id": "33",  # Manchester United
        "name": "Manchester United", 
        "type": "team",
        "rival_name": "Manchester City",
        "supported_team": "Manchester City",  # This is who we support/motivate for
        "target_username": "fulltimedevils"  # Man United fan page - gets notified when Man City wins
    }
]

# Helper function to find rivalry by ID
def find_rivalry(entity_id):
    """Find rivalry configuration by player or team ID."""
    for rivalry in RIVALRIES:
        if rivalry["id"] == str(entity_id):
            return rivalry
    return None

def get_fan_to_notify(entity_id):
    """Returns the fan's username to notify for a given player or team."""
    rivalry = find_rivalry(entity_id)
    if not rivalry:
        return None
    return rivalry.get("target_username")

def get_rival_name(entity_id):
    """Returns the rival's name for a given player or team."""
    rivalry = find_rivalry(entity_id)
    if not rivalry:
        return None
    return rivalry.get("rival_name")

def get_supported_entity(entity_id):
    """Returns who the fan supports (used for motivation messages)."""
    rivalry = find_rivalry(entity_id)
    if not rivalry:
        return None
    
    if rivalry["type"] == "player":
        return rivalry.get("supported_player")
    else:  # team
        return rivalry.get("supported_team")

def is_player(entity_id):
    """Check if the entity is a player."""
    rivalry = find_rivalry(entity_id)
    return rivalry and rivalry["type"] == "player"

def is_team(entity_id):
    """Check if the entity is a team.""" 
    rivalry = find_rivalry(entity_id)
    return rivalry and rivalry["type"] == "team"