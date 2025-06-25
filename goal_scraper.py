# goal_scraper.py
import requests
import time
import os
import json
from dotenv import load_dotenv
from rivals import RIVALRIES, get_fan_to_notify, get_rival_name, get_supported_entity, is_player, is_team
import dm_sender # This is our other file
import argparse

# Load environment variables from .env file
load_dotenv()

# --- CONFIGURATION ---
# API keys loaded from .env file
API_KEY = os.getenv("FOOTBALL_API_KEY", "39d9a4825a5975f6fd0f7b9969ad5fd7")  # Fallback to hardcoded if not in .env
API_HOST = "v3.football.api-sports.io"

# OpenAI Configuration - Add your OpenAI API key to .env file
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Will load from .env file
USE_OPENAI = True  # Set to False to use only fallback messages

# The season you want to track. Update this as new seasons start.
SEASON = "2024"  # Updated to 2024 season 
HEADERS = {
    'x-rapidapi-host': API_HOST,
    'x-rapidapi-key': API_KEY
}
# Simple in-memory "databases" to store the last known counts
PLAYER_GOAL_STATE = {}  # For individual players (goals)
TEAM_WIN_STATE = {}     # For teams (wins)

def get_total_goals(player_id):
    """
    Calls the API and calculates the total goals for a player across all competitions for the season.
    """
    url = f"https://{API_HOST}/players"
    params = {"id": player_id, "season": SEASON}
    
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status() # Raises an error for bad responses (4xx or 5xx)
        
        data = response.json()
        
        if not data['response']:
            print(f"  - Warning: No data returned for player {player_id} for season {SEASON}.")
            return 0

        total_goals = 0
        player_stats = data['response'][0]['statistics']
        for stats_by_league in player_stats:
            goals = stats_by_league['goals']['total']
            if goals is not None:
                total_goals += goals
        
        return total_goals
        
    except requests.exceptions.RequestException as e:
        print(f"  - Error fetching data from API: {e}")
        return None # Return None to indicate the API call failed

def get_team_wins(team_id):
    """
    Calls the API and gets the total wins for a team in the Premier League for the season.
    """
    url = f"https://{API_HOST}/teams/statistics"
    params = {"team": team_id, "season": SEASON, "league": "39"}  # Premier League
    
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        
        data = response.json()
        print(f"  - Debug: Team {team_id} API response: {data}")  # Debug line
        
        if not data['response']:
            print(f"  - Warning: No data returned for team {team_id} for season {SEASON}.")
            return 0

        team_stats = data['response']
        wins = team_stats['fixtures']['wins']['total']
        
        return wins if wins is not None else 0
        
    except requests.exceptions.RequestException as e:
        print(f"  - Error fetching team data from API: {e}")
        return None

def initialize_states():
    """Fills the initial state for all players and teams in our rivalry table."""
    print("Initializing player/team states...")
    for rivalry in RIVALRIES:
        entity_id = rivalry["id"]
        entity_name = rivalry["name"]
        entity_type = rivalry["type"]
        
        if entity_type == "player":
            goals = get_total_goals(entity_id)
            if goals is not None:
                PLAYER_GOAL_STATE[entity_id] = goals
                print(f"  - Initial goals for {entity_name} (player, {SEASON}): {goals}")
            else:
                print(f"Could not fetch initial state for {entity_name}. Exiting.")
                exit()
        elif entity_type == "team":
            wins = get_team_wins(entity_id)
            if wins is not None:
                TEAM_WIN_STATE[entity_id] = wins
                print(f"  - Initial wins for {entity_name} (team, {SEASON}): {wins}")
            else:
                print(f"Could not fetch initial state for {entity_name}. Exiting.")
                exit()
        
        time.sleep(5) # Add a small delay to be kind to the API

def generate_banter_message(scorer_name, supported_entity, current_count, entity_type):
    """
    Generate a dynamic banter message using OpenAI API.
    Falls back to pre-written messages if API fails.
    """
    # Check if we should use OpenAI and if API key is configured
    if not USE_OPENAI or not OPENAI_API_KEY:
        print("  - Using fallback messages (OpenAI not configured)")
        return generate_fallback_message(scorer_name, supported_entity, current_count, entity_type)
    
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        activity = "goals" if entity_type == "player" else "wins"
        activity_singular = "goal" if entity_type == "player" else "win"
        
        prompt = f"""Generate a fun, playful, and banterous social media message for football/soccer fans. 

Context:
- {scorer_name} just scored a {activity_singular} (now has {current_count} {activity} this season)
- This message is being sent to fans of {supported_entity} (the rival team/player)
- Keep it light-hearted, funny, and engaging - good-natured trolling
- Use emojis and make it social media friendly
- Include relevant hashtags
- Maximum 280 characters to fit social media limits
- Don't be mean-spirited, keep it playful and fun
- The tone should be like friendly banter between football fans at a pub - cheeky but not nasty

Generate ONLY the message text, no explanations or quotes around it."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.8
        )
        
        message_content = response.choices[0].message.content
        if message_content:
            message = message_content.strip()
            print(f"  - Generated OpenAI message: {message[:50]}...")
            return message
        else:
            print("  - OpenAI returned empty response. Using fallback message.")
            return generate_fallback_message(scorer_name, supported_entity, current_count, entity_type)
        
    except ImportError:
        print("  - OpenAI package not installed. Using fallback messages.")
        return generate_fallback_message(scorer_name, supported_entity, current_count, entity_type)
    except Exception as e:
        print(f"  - OpenAI API failed: {e}. Using fallback message.")
        return generate_fallback_message(scorer_name, supported_entity, current_count, entity_type)

def generate_fallback_message(scorer_name, supported_entity, current_count, entity_type):
    """
    Enhanced fallback messages with more variety and randomness.
    """
    import random
    
    if entity_type == "team":
        # Team banter messages with more variety
        banter_templates = [
            "🔥 {scorer} just bagged WIN #{count}! 📈\n\nMeanwhile {rival} fans are probably {action} 😅\n\nTime to step up! 💪⚽\n\n{hashtags}",
            
            "🚨 BREAKING: {scorer} Alert! 🚨\n\n{scorer}: {count} wins ✅\n{rival} fans: {status} ⏰\n\n{encouragement} 😂🏆\n\n{hashtags}",
            
            "📊 STATS UPDATE 📊\n\n{scorer} wins: {count} 🔥\n{rival} fans' {emotion}: {trend} 📉\n\n{consolation} 💙❤️\n\n{hashtags}",
            
            "🎯 {scorer} just hit WIN #{count}! 🎉\n\n{rival} fans are probably {reaction} 📱💔\n\n{message} ⚽✨\n\n{hashtags}"
        ]
        
        # Random elements for variety
        actions = ["stress-eating", "refreshing the table", "checking if VAR exists", "googling 'how to support a winning team'"]
        statuses = ["Still waiting...", "Still dreaming...", "Still hoping...", "Still believing..."]
        encouragements = ["Don't worry, there's always next season!", "At least you tried!", "Better luck next time!", "The hope is admirable!"]
        emotions = ["hopes", "dreams", "confidence", "expectations"]
        trends = ["Declining", "Fading", "Vanishing", "Disappearing"]
        consolations = ["But hey, at least you've got passion!", "At least the memes are good!", "The banter makes it worth it!", "You'll always have the memories!"]
        reactions = ["googling 'how to delete Twitter'", "checking if this is a simulation", "wondering if they're still dreaming", "looking for the unsubscribe button"]
        messages = ["Stay strong, rivals! Football is beautiful!", "The banter makes football amazing!", "Rivalry makes the game special!", "This is why we love football!"]
        
    else:
        # Player banter messages
        banter_templates = [
            "🐐 {scorer} just scored GOAL #{count}! 🔥⚽\n\n{rival} fans are like '{reaction}' 😂\n\n{message} ☕⚽\n\n{hashtags}",
            
            "🚀 {scorer} STRIKES AGAIN! 🚀\n\n{scorer}: {count} goals 📈\n{rival} fans: {excuse} 🤷‍♂️\n\n{comment} 😄⚽\n\n{hashtags}",
            
            "📈 STONKS! 📈\n\n{scorer} goals: {count} ↗️\n{rival} confidence: {status} ↘️\n\n{suggestion} 🎮😂\n\n{hashtags}",
            
            "🎪 {scorer} goal #{count}! 🎯\n\n{rival} fans: {gymnastics} 🤸‍♂️\n\n{quote} 😂\n\nLove you really! ❤️⚽\n\n{hashtags}"
        ]
        
        reactions = ["Wait, football is still happening?", "Is this real life?", "Did someone say football?", "Oh right, there's a game on!"]
        excuses = ["Still making excuses", "Blaming the weather", "Questioning the referee", "Checking the offside rule"]
        comments = ["Football is beautiful, isn't it?", "The beautiful game continues!", "This is why we love football!", "Poetry in motion!"]
        statuses = ["Declining", "Fading", "Evaporating", "In freefall"]
        suggestions = ["Don't worry, there's always FIFA!", "At least you have video games!", "YouTube highlights are free!", "There's always next season!"]
        gymnastics = ["Performing mental gymnastics", "Doing backflips to explain this", "In full denial mode", "Rewriting the rulebook"]
        quotes = ['"It was offside!" "The grass was too long!"', '"The ball was too round!"', '"It\'s all rigged!"', '"That doesn\'t count because..."']
        
        actions = reactions
        encouragements = comments
        consolations = suggestions
        messages = comments
    
    # Select random template and elements
    template = random.choice(banter_templates)
    
    # Common hashtags
    hashtags_options = [
        "#Football #Banter #Rivalry",
        "#BanterFC #Football #Reality", 
        "#FootballBanter #Rivalry #Love",
        "#Goals #Football #BanterTime",
        "#ManchesterDerby #Football #Banter" if "Manchester" in scorer_name or "Manchester" in supported_entity else "#Football #Banter #Rivalry"
    ]
    
    # Fill in the template
    message = template.format(
        scorer=scorer_name,
        rival=supported_entity,
        count=current_count,
        action=random.choice(actions) if 'action' in template else '',
        status=random.choice(statuses) if 'status' in template else '',
        encouragement=random.choice(encouragements) if 'encouragement' in template else '',
        emotion=random.choice(emotions) if 'emotion' in template else '',
        trend=random.choice(trends) if 'trend' in template else '',
        consolation=random.choice(consolations) if 'consolation' in template else '',
        reaction=random.choice(reactions) if 'reaction' in template else '',
        message=random.choice(messages) if 'message' in template else '',
        excuse=random.choice(excuses) if 'excuse' in template else '',
        comment=random.choice(comments) if 'comment' in template else '',
        suggestion=random.choice(suggestions) if 'suggestion' in template else '',
        gymnastics=random.choice(gymnastics) if 'gymnastics' in template else '',
        quote=random.choice(quotes) if 'quote' in template else '',
        hashtags=random.choice(hashtags_options)
    )
    
    return message

def check_for_new_activity():
    """The main function to check for new goals/wins and trigger DMs."""
    print(f"\n[{time.ctime()}] Checking for new activity...")
    for rivalry in RIVALRIES:
        entity_id = rivalry["id"]
        entity_name = rivalry["name"]
        entity_type = rivalry["type"]
        
        # Get current count based on entity type
        if entity_type == "player":
            current_count = get_total_goals(entity_id)
            last_known_count = PLAYER_GOAL_STATE.get(entity_id, 0)
            activity_word = "goal"
            activity_plural = "goals"
        elif entity_type == "team":
            current_count = get_team_wins(entity_id)
            last_known_count = TEAM_WIN_STATE.get(entity_id, 0)
            activity_word = "win"
            activity_plural = "wins"
        else:
            continue
        
        # Ensure we got a valid response before comparing
        if current_count is None:
            print(f"  - Skipping check for {entity_name} due to API error.")
            continue

        if current_count > last_known_count:
            print(f"  >>> {activity_word.upper()} DETECTED for {entity_name} ({entity_type})!")
            
            fan_to_notify = get_fan_to_notify(entity_id)
            
            if fan_to_notify:
                # Generate a dynamic banter message
                message = generate_banter_message(entity_name, get_supported_entity(entity_id), current_count, entity_type)
                
                # Call the DM sender
                dm_sender.send_rival_dm_sync(
                    recipient_username=fan_to_notify,
                    message=message
                )
            
            # IMPORTANT: Update the state with the new count
            if entity_type == "player":
                PLAYER_GOAL_STATE[entity_id] = current_count
            elif entity_type == "team":
                TEAM_WIN_STATE[entity_id] = current_count
        else:
            activity_type = activity_plural if entity_type == "player" else activity_plural
            print(f"  - No new {activity_type} for {entity_name} ({entity_type}). (Current: {current_count})")

        # Be respectful of the API's rate limits.
        # Free plans are often limited per minute or per day.
        time.sleep(10) # 10-second delay between checking each entity

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--simulate-goal", action="store_true", help="Simulate a goal/win event for testing.")
    args = parser.parse_args()

    initialize_states()

    if args.simulate_goal:
        # Simulate activity for both players and teams
        print("[TEST MODE] Simulating new activity...")
        
        for rivalry in RIVALRIES:
            entity_id = rivalry["id"]
            entity_name = rivalry["name"]
            entity_type = rivalry["type"]
            
            if entity_type == "player" and entity_id in PLAYER_GOAL_STATE:
                # Decrease goal count by 1 to simulate a new goal being detected
                PLAYER_GOAL_STATE[entity_id] = max(0, PLAYER_GOAL_STATE[entity_id] - 1)
                print(f"[TEST MODE] Simulated a new goal for {entity_name} (player).")
            elif entity_type == "team" and entity_id in TEAM_WIN_STATE:
                # Decrease win count by 1 to simulate a new win being detected
                TEAM_WIN_STATE[entity_id] = max(0, TEAM_WIN_STATE[entity_id] - 1)
                print(f"[TEST MODE] Simulated a new win for {entity_name} (team).")

    while True:
        check_for_new_activity()
        # Check every 5 minutes. 100 requests/day allows for checks every ~15 mins.
        # Adjust as needed based on your API plan.
        print("\n--- Waiting for next check cycle ---")
        time.sleep(300)