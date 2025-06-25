# 🏆 DMotivator: AI-Powered Football Rivalry Bot

**Instagram DM MCP Hackathon Submission** 🧨

An unhinged football rivalry bot that monitors real-time player goals and team wins, then sends AI-generated banter messages to rival fans via Instagram DMs using the Model Context Protocol (MCP).

## 🎯 Hackathon Challenge

This project was built for the **Instagram DM MCP Hackathon** - leveraging the open-sourced MCP server to create something wild with Instagram DMs. Our bot automatically trolls rival football fans with personalized, AI-generated banter whenever their rivals score or win.

## 🚀 How It Works

### The Magic Behind DMotivator

1. **Real-Time Sports Monitoring**: Continuously monitors football APIs for player goals and team wins
2. **AI-Powered Banter Generation**: Uses OpenAI GPT to create unique, contextual trash talk messages
3. **Instagram DM Automation**: Sends personalized messages to rival fans via MCP-powered Instagram integration
4. **Smart Rivalry Management**: Tracks multiple player and team rivalries with sophisticated state management

### Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Goal Scraper  │───▶│   MCP Server     │───▶│  Instagram DMs  │
│   (Monitor API) │    │   (Enhanced)     │    │   (Rival Fans)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Rivals.py     │    │   OpenAI GPT     │    │   Fan Pages     │
│ (Rivalry Logic) │    │ (Banter Engine)  │    │ (@cr7ir, etc.)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🎮 Current Rivalries

### Player Rivalries
- **Lionel Messi vs Cristiano Ronaldo**
  - When Messi scores → Messages `@cr7ir` (Ronaldo fan page)
  - When Ronaldo scores → Messages `@we.are.messi` (Messi fan page)

### Team Rivalries (Manchester Derby)
- **Manchester City vs Manchester United**
  - When Man City wins → Messages `@fulltimedevils` (Man United fan page)
  - When Man United wins → Messages `@mancity_mcfc` (Man City fan page)

## 🔧 Key Enhancements to Original MCP Server

### 1. **Session Management & Rate Limiting**
```python
# Added persistent session handling to prevent Instagram rate limiting
def load_session():
    """Load saved Instagram session to avoid repeated logins"""
    if os.path.exists(SESSION_FILE):
        try:
            client.load_settings(SESSION_FILE)
            client.login(username, password)
            return True
        except Exception as e:
            print(f"Failed to load session: {e}")
    return False
```

### 2. **Enhanced Error Handling & Retry Logic**
```python
def send_rival_dm_sync(recipient_username, message):
    """Enhanced DM sending with exponential backoff and retry logic"""
    max_retries = 3
    base_delay = 1
    
    for attempt in range(max_retries):
        try:
            result = send_dm_via_mcp(recipient_username, message)
            if result.get("success"):
                return result
        except Exception as e:
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)
```

### 3. **Proper MCP Protocol Implementation**
```python
def initialize_mcp():
    """Fixed MCP initialization sequence - CRITICAL FIX!"""
    # Send initialize request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "clientInfo": {"name": "dm-motivator", "version": "1.0.0"}
        }
    }
    
    response = send_request(init_request)
    
    # Send initialized notification (this was missing in original!)
    initialized_notification = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    }
    send_notification(initialized_notification)
```

## 🤖 AI-Powered Banter Engine

### Dynamic Message Generation
Unlike static templates, our bot uses OpenAI GPT to generate contextual, unique banter:

```python
def generate_banter_message(scorer_name, supported_entity, current_count, entity_type):
    """Generate dynamic banter using OpenAI with fallback to enhanced templates"""
    
    prompt = f"""Generate a fun, playful, and banterous social media message for football fans. 

Context:
- {scorer_name} just scored (now has {current_count} goals/wins this season)
- This message is being sent to fans of {supported_entity} (the rival)
- Keep it light-hearted, funny, and engaging - good-natured trolling
- Use emojis and make it social media friendly
- Maximum 280 characters
- The tone should be like friendly banter between football fans at a pub

Generate ONLY the message text."""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150,
        temperature=0.8
    )
```

### Sample Generated Messages
- **To Ronaldo fans when Messi scores**: "Hey Ronaldo fans, looks like Messi is on 🔥 with 27 goals this season! Someone better tell CR7 to step up his game 🤣⚽️ #MessiMagic"
- **To Man United fans when City wins**: "Hey Manchester United fans, just a reminder that Manchester City now has 22 wins this season... 🏆⚽️ Better luck next time! #ManchesterDerby"

## 📊 Real-Time Sports Integration

### Multi-Source Data Tracking
- **Player Goals**: Aggregates goals across all competitions using API-Sports
- **Team Wins**: Tracks Premier League wins specifically (not just goals)
- **Smart State Management**: Separate tracking for players vs teams

### Supported Data Sources
- **API-Sports**: Primary football data provider
- **Real-time monitoring**: Checks every 5 minutes
- **Multi-league support**: Tracks across different competitions

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd mcpdmotivator
```

### 2. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the project root:
```env
# OpenAI API Key (get from https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Football API Key (get from https://www.api-football.com/)
FOOTBALL_API_KEY=your-football-api-key-here

# Instagram Credentials for your bot account
INSTAGRAM_USERNAME=your-instagram-bot-account
INSTAGRAM_PASSWORD=your-instagram-password
```

### 4. Verify Setup
Run the verification script to check your configuration:
```bash
python3 setup_verification.py
```

This will check:
- ✅ All dependencies are installed
- ✅ Environment variables are configured
- ✅ OpenAI API connection works
- ✅ Football API connection works
- ✅ Rivalry configuration is valid

### 5. Start the MCP Server

The MCP server handles Instagram DM communication. It needs to run **before** starting the goal scraper.

```bash
python3 mcp_server.py --username your-instagram-username --password your-instagram-password
```

**Important Notes:**
- Use a dedicated Instagram account for the bot (not your personal account)
- The server will create a session file (e.g., `username_session.json`) to avoid repeated logins
- Keep the MCP server running in one terminal while you run the goal scraper in another
- If Instagram blocks the login, wait a few hours and try again

### 6. Run the Goal Scraper

**In a separate terminal**, run the goal scraper:

```bash
# Test mode (simulates goals/wins)
python3 goal_scraper.py --simulate-goal

# Production mode (continuous monitoring)
python3 goal_scraper.py
```

## 🔄 How the Two-Part System Works

### MCP Server (`mcp_server.py`)
- **Purpose**: Handles Instagram authentication and DM sending
- **Runs**: Continuously in the background
- **Session Management**: Saves Instagram login session to avoid rate limiting
- **Protocol**: Implements Model Context Protocol for communication

### Goal Scraper (`goal_scraper.py`) 
- **Purpose**: Monitors sports APIs and triggers DM sending
- **Runs**: Either once (simulation) or continuously (production)
- **Communication**: Sends requests to MCP server when goals/wins detected
- **AI Integration**: Generates dynamic banter messages via OpenAI

### Session Files Explained

When you first run the MCP server, it will:
1. Log into Instagram with your credentials
2. Save the session to `{username}_session.json`
3. Reuse this session for future runs to avoid Instagram rate limiting

**The session file contains:**
- Instagram authentication tokens
- Client session IDs
- Device information

⚠️ **Security**: Keep session files private - they contain authentication data!

## 🎮 Usage Examples

### Testing the System
```bash
# Simulate goals and wins to test the entire pipeline
python3 goal_scraper.py --simulate-goal
```

### Adding New Rivalries
Edit `rivals.py` to add new player or team rivalries:
```python
{
    "id": "new-player-id",
    "name": "Player Name",
    "type": "player",
    "rival_name": "Rival Name",
    "supported_player": "Who to promote",
    "target_username": "fan_page_username"
}
```

### Monitoring Logs
The system provides detailed logging:
- API call status
- Message generation (OpenAI vs fallback)
- Instagram DM delivery status
- Error handling and retries

## 🛡️ Security & Best Practices

### Rate Limiting
- Built-in delays between API calls (10 seconds)
- Instagram session persistence to avoid repeated logins
- Exponential backoff on failures

### Error Handling
- Graceful degradation when APIs are unavailable
- Fallback to enhanced template messages if OpenAI fails
- Comprehensive logging for debugging

### Privacy
- No storage of Instagram credentials (loaded from .env)
- Session files for Instagram authentication
- API keys managed via environment variables

## 📁 Project Structure

```
mcpdmotivator/
├── goal_scraper.py          # Main monitoring script
├── mcp_server.py           # Enhanced MCP server
├── dm_sender.py            # Instagram DM client
├── rivals.py               # Rivalry configuration
├── setup_verification.py   # Setup verification script
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
├── dm_otivator_session.json # Instagram session (auto-generated)
└── README.md              # This file
```

## 🏆 Hackathon Innovation

### What Makes This Special

1. **Multi-Modal AI Integration**: Combines real-time sports data with AI-generated content
2. **Advanced MCP Usage**: Goes beyond simple messaging to create a complete automated system
3. **Intelligent Targeting**: Contextual rivalry management with personalized messaging
4. **Production-Ready**: Includes session management, error handling, and rate limiting
5. **Scalable Architecture**: Easy to add new rivalries, sports, or platforms

### Technical Achievements

- ✅ **Fixed Critical MCP Protocol Issues**: Proper initialization sequence
- ✅ **Enhanced Session Management**: Persistent Instagram sessions
- ✅ **AI-Powered Content Generation**: Dynamic, contextual messages
- ✅ **Multi-Entity Tracking**: Both individual players and teams
- ✅ **Robust Error Handling**: Production-ready reliability

## 🚀 Future Enhancements

### Potential Expansions
- **More Sports**: Basketball, American Football, Tennis rivalries
- **More Platforms**: Twitter, TikTok, Discord integration
- **Advanced AI**: Context-aware messages based on match importance
- **User Interaction**: Respond to replies and comments
- **Analytics**: Track engagement and message effectiveness

### Scaling Opportunities
- **Multi-language Support**: Generate banter in different languages
- **Custom Rivalries**: User-defined rivalry creation
- **Real-time Notifications**: Instant alerts for major events
- **Social Media Integration**: Cross-platform posting

## 🎯 Impact & Vision

This bot represents the future of sports engagement - where AI meets real-time data to create personalized, contextual interactions. It's not just about sending messages; it's about creating moments of joy, rivalry, and community in the digital sports world.

**The result?** A bot that doesn't just notify - it entertains, engages, and brings the passion of football rivalry into the digital age with style and humor! 🏆⚽️

## 📞 Support & Contributing

### Issues
If you encounter any issues, please check:
1. API keys are correctly set in `.env`
2. Instagram credentials are valid
3. MCP server is running before starting goal scraper

### Contributing
Contributions are welcome! Areas for improvement:
- Additional sports and leagues
- Enhanced AI prompt engineering
- Better error handling
- Performance optimizations

## 🔒 Security & Privacy

### Protected Files
The `.gitignore` file ensures these sensitive files are **never** committed to version control:
- `.env` - Contains your API keys and Instagram credentials
- `*_session.json` - Instagram authentication sessions
- `__pycache__/` - Python cache files

### Best Practices
- **Never commit API keys** or passwords to git
- **Use a dedicated Instagram account** for the bot (not your personal account)
- **Keep session files secure** - they can be used to access your Instagram account
- **Rotate API keys** periodically for better security

---

*Built for the Instagram DM MCP Hackathon - Where AI meets football passion!* 🧨

**Let the banter begin!** ⚽️🤖 