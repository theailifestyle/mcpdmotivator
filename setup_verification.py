#!/usr/bin/env python3
"""
Setup Verification Script for DMotivator
Helps users verify their installation and configuration before running the bot.
"""

import os
import sys
from dotenv import load_dotenv

def check_dependencies():
    """Check if all required packages are installed."""
    print("🔍 Checking dependencies...")
    required_packages = [
        'requests', 'openai', 'instagrapi', 'fastmcp', 
        'dotenv', 'pydantic'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip3 install -r requirements.txt")
        return False
    
    print("✅ All dependencies installed!")
    return True

def check_env_file():
    """Check if .env file exists and has required variables."""
    print("\n🔍 Checking .env configuration...")
    
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Create a .env file with:")
        print("OPENAI_API_KEY=your-openai-key")
        print("FOOTBALL_API_KEY=your-football-api-key")
        print("INSTAGRAM_USERNAME=your-instagram-username")
        print("INSTAGRAM_PASSWORD=your-instagram-password")
        return False
    
    load_dotenv()
    
    required_vars = [
        'OPENAI_API_KEY',
        'FOOTBALL_API_KEY', 
        'INSTAGRAM_USERNAME',
        'INSTAGRAM_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value == 'your-openai-api-key-here':
            print(f"  ❌ {var} - MISSING or placeholder")
            missing_vars.append(var)
        else:
            print(f"  ✅ {var} - Set")
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ Environment configuration complete!")
    return True

def test_openai_connection():
    """Test OpenAI API connection."""
    print("\n🔍 Testing OpenAI connection...")
    
    try:
        from openai import OpenAI
        load_dotenv()
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ OpenAI API key not found in .env")
            return False
        
        client = OpenAI(api_key=api_key)
        
        # Simple test request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'OpenAI connection test successful!'"}],
            max_tokens=10
        )
        
        if response.choices[0].message.content:
            print("✅ OpenAI connection successful!")
            return True
        else:
            print("❌ OpenAI returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI connection failed: {e}")
        return False

def test_football_api():
    """Test Football API connection."""
    print("\n🔍 Testing Football API connection...")
    
    try:
        import requests
        load_dotenv()
        
        api_key = os.getenv('FOOTBALL_API_KEY')
        if not api_key:
            print("❌ Football API key not found in .env")
            return False
        
        headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': api_key
        }
        
        # Test with a simple request
        response = requests.get(
            "https://v3.football.api-sports.io/players",
            headers=headers,
            params={"id": "154", "season": "2024"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('response'):
                print("✅ Football API connection successful!")
                return True
            else:
                print("❌ Football API returned no data")
                return False
        else:
            print(f"❌ Football API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Football API connection failed: {e}")
        return False

def test_rivalry_config():
    """Test rivalry configuration."""
    print("\n🔍 Testing rivalry configuration...")
    
    try:
        from rivals import RIVALRIES, get_fan_to_notify, get_supported_entity
        
        if not RIVALRIES:
            print("❌ No rivalries configured")
            return False
        
        print(f"✅ Found {len(RIVALRIES)} rivalries:")
        for rivalry in RIVALRIES:
            name = rivalry.get('name', 'Unknown')
            target = rivalry.get('target_username', 'Unknown')
            entity_type = rivalry.get('type', 'Unknown')
            print(f"  - {name} ({entity_type}) → @{target}")
        
        return True
        
    except Exception as e:
        print(f"❌ Rivalry configuration error: {e}")
        return False

def main():
    """Run all verification checks."""
    print("🏆 DMotivator Setup Verification")
    print("=" * 50)
    
    checks = [
        check_dependencies,
        check_env_file,
        test_openai_connection,
        test_football_api,
        test_rivalry_config
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All checks passed! Your DMotivator is ready to run!")
        print("\nNext steps:")
        print("1. Start MCP server: python3 mcp_server.py --username <instagram> --password <password>")
        print("2. Test the bot: python3 goal_scraper.py --simulate-goal")
        print("3. Run production: python3 goal_scraper.py")
    else:
        print("❌ Some checks failed. Please fix the issues above before running DMotivator.")
        sys.exit(1)

if __name__ == "__main__":
    main() 