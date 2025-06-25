# Demo Setup Guide for MCP DM Motivator

This guide will help you set up and run a demo of the MCP DM Motivator system with 4 different scenarios.

## Demo Overview

The demo simulates 4 different scenarios:
1. **Messi scoring a goal** → Sends DM to `demo_ronaldo_fan`
2. **Ronaldo scoring a goal** → Sends DM to `demo_messi_fan`
3. **Manchester United winning** → Sends DM to `demo_city_fan`
4. **Manchester City winning** → Sends DM to `demo_united_fan`

## Pre-Demo Setup

### 1. Instagram Accounts Required

You'll need to set up 5 Instagram accounts:

**Main Account (sends DMs):**
- Username: `demo_motivator_2024` (or your chosen demo account)
- Password: `YOUR_SECURE_PASSWORD` (replace with your actual password)

**Target Accounts (receive DMs):**
- `demo_ronaldo_fan` - Receives DMs when Messi scores
- `demo_messi_fan` - Receives DMs when Ronaldo scores  
- `demo_city_fan` - Receives DMs when Manchester United wins
- `demo_united_fan` - Receives DMs when Manchester City wins

### 2. Account Setup Tips

1. **Create all accounts** using different email addresses
2. **Follow each other** - Have the main account follow all target accounts
3. **Send initial messages** - Send a test message from main account to each target to establish chat threads
4. **Use real profile pictures** and bio information to avoid being flagged as spam

### 3. Environment Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables for security:**
```bash
# Copy the example environment file
cp env_example.txt .env

# Edit the .env file with your actual credentials
# NEVER commit the .env file to version control!
```

3. **Configure your .env file:**
```
DEMO_INSTAGRAM_USERNAME=your_actual_demo_username
DEMO_INSTAGRAM_PASSWORD=your_actual_demo_password
FOOTBALL_API_KEY=your_football_api_key
OPENAI_API_KEY=your_openai_key_optional
```

## Running the Demo

### Option 1: Full Demo Script (Recommended)

Run the automated demo script that will execute all 4 scenarios:

```bash
python3 demo_simulator.py
```

This will:
- Show you what scenarios will be run
- Wait for your confirmation
- Execute each scenario with a 10-second delay between them
- Show the generated messages and send status

### Option 2: Manual Individual Tests

You can test individual scenarios by modifying the goal_scraper.py:

```bash
# Test Messi scoring
python3 goal_scraper.py --simulate-goal

# Or modify the script to test specific scenarios
```

## Demo Flow

Each scenario follows this flow:

1. **Scenario Introduction** - Shows which scenario is running
2. **Target Identification** - Shows which fan page will receive the DM
3. **Message Generation** - Creates a banter message using AI or fallback templates
4. **Message Display** - Shows the generated message
5. **DM Sending** - Sends the message via Instagram DM
6. **Status Report** - Shows success/failure status

## Expected Output

For each scenario, you should see output like:

```
============================================================
🎬 DEMO SCENARIO: Messi scores a goal! 🐐⚽
============================================================
📱 Target fan page: demo_ronaldo_fan
🎯 Entity: Lionel Messi (player)
🏆 Supported entity: Cristiano Ronaldo
💬 Generating banter message...
📝 Generated message:
   🐐 Lionel Messi just scored GOAL #5! 🔥⚽
   
   Cristiano Ronaldo fans are like 'Wait, football is still happening?' 😂
   
   Football is beautiful, isn't it? ☕⚽
   
   #Football #Banter #Rivalry
🚀 Sending DM to demo_ronaldo_fan...
✅ MCP server started
✅ Initialize request successful
✅ Initialized notification sent
✅ DM sent successfully to demo_ronaldo_fan via MCP
✅ Demo scenario completed successfully!
⏳ Waiting 10 seconds before next scenario...
```

## Troubleshooting

### Common Issues:

1. **Instagram Login Fails**
   - Check username/password in `dm_sender.py`
   - Make sure account isn't locked or requires verification
   - Try logging in manually first

2. **DM Sending Fails**
   - Ensure target accounts exist and are followable
   - Check if accounts have been flagged for spam
   - Verify chat threads exist between accounts

3. **MCP Server Issues**
   - Check that `fastmcp` and `instagrapi` are installed
   - Verify Python version compatibility
   - Look for session files that might be corrupted

### Debug Mode

To see more detailed output, you can modify the scripts to include more logging or run components individually.

## Security Notes

🔒 **Important Security Reminders:**
- Never commit your `.env` file to version control
- Use strong, unique passwords for all demo accounts
- Consider using temporary accounts that you can delete after the demo
- The `.gitignore` file is already configured to exclude credential files

## Post-Demo Cleanup

After the demo:
1. You can keep the accounts for future demos
2. Or delete the demo accounts if no longer needed
3. Revert `dm_sender.py` and `rivals.py` to production settings
4. Consider rotating passwords if accounts will be reused

## Recording the Demo

For screen recording:
1. Start recording before running `python3 demo_simulator.py`
2. Show the terminal output clearly
3. Switch to Instagram to show the received DMs
4. Demonstrate the different message types for each scenario

The entire demo should take about 2-3 minutes to complete all 4 scenarios. 