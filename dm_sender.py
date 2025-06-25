# dm_sender.py
import json
import subprocess
import sys
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MCPClient:
    def __init__(self, server_command: list):
        self.server_command = server_command
        self.process = None
        self.message_id = 1

    def start_server(self):
        try:
            self.process = subprocess.Popen(
                self.server_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            print("✅ MCP server started")
            return True
        except Exception as e:
            print(f"❌ Failed to start MCP server: {e}")
            return False

    def send_message(self, message: dict) -> dict:
        if not self.process:
            return {"success": False, "message": "MCP server not running"}
        try:
            message_str = json.dumps(message) + "\n"
            if self.process and self.process.stdin:
                self.process.stdin.write(message_str)
                self.process.stdin.flush()
            if self.process and self.process.stdout:
                response = self.process.stdout.readline()
                if response:
                    return {"success": True, "response": json.loads(response)}
                else:
                    return {"success": False, "message": "No response from server"}
            else:
                return {"success": False, "message": "No stdout available"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def initialize_mcp(self):
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": self.message_id,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "mcpdmotivator", "version": "1.0.0"}
            }
        }
        result = self.send_message(init_request)
        if not result["success"]:
            print(f"❌ Initialize request failed: {result}")
            return False
        
        # Check if we got a proper initialize response
        if "response" not in result or "result" not in result["response"]:
            print(f"❌ Invalid initialize response: {result}")
            return False
            
        print("✅ Initialize request successful")
        self.message_id += 1
        
        # Send initialized notification (no response expected)
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        
        try:
            message_str = json.dumps(initialized_notification) + "\n"
            if self.process and self.process.stdin:
                self.process.stdin.write(message_str)
                self.process.stdin.flush()
                print("✅ Initialized notification sent")
                return True
            else:
                print("❌ No stdin available for initialized notification")
                return False
        except Exception as e:
            print(f"❌ Failed to send initialized notification: {e}")
            return False

    def call_tool(self, tool_name: str, arguments: dict) -> dict:
        tool_request = {
            "jsonrpc": "2.0",
            "id": self.message_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        result = self.send_message(tool_request)
        self.message_id += 1
        if result["success"] and "response" in result:
            response = result["response"]
            if "result" in response:
                return {"success": True, "result": response["result"]}
            elif "error" in response:
                return {"success": False, "message": response["error"].get("message", "Unknown error")}
        return result

    def stop_server(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
            print("✅ MCP server stopped")

def send_rival_dm(recipient_username, message):
    """
    Sends a DM via the MCP server using the MCP protocol.
    """
    command = {
        "tool": "send_message",
        "args": {
            "username": recipient_username,
            "message": message
        }
    }
    print("\n--- Preparing to send DM ---")
    print(json.dumps(command, indent=2))
    print("---------------------------\n")
    # Get credentials from environment variables for security
    instagram_username = os.getenv("INSTAGRAM_USERNAME", "your_instagram_username")
    instagram_password = os.getenv("INSTAGRAM_PASSWORD", "your_instagram_password")
    
    server_command = [
        "python3",
        "mcp_server.py",
        "--username", instagram_username,
        "--password", instagram_password
    ]
    client = MCPClient(server_command)
    if not client.start_server():
        print(f"❌ Failed to start MCP server")
        return
    try:
        print(f"🚀 Attempting to send DM to {recipient_username} via MCP...")
        time.sleep(2)
        if not client.initialize_mcp():
            print(f"❌ Failed to initialize MCP connection")
            return
        print("✅ MCP connection initialized")
        result = client.call_tool("send_message", {
            "username": recipient_username,
            "message": message
        })
        if result.get("success"):
            print(f"✅ DM sent successfully to {recipient_username} via MCP")
            if "result" in result:
                print(f"MCP Response: {result['result']}")
        else:
            print(f"❌ Failed to send DM via MCP: {result.get('message', 'Unknown error')}")
            print(f"📋 MCP Command that was attempted:")
            print(json.dumps(command, indent=2))
    except Exception as e:
        print(f"❌ Error sending DM via MCP: {e}")
        print(f"📋 MCP Command to execute:")
        print(json.dumps(command, indent=2))
    finally:
        client.stop_server()

def send_rival_dm_sync(recipient_username, message):
    """
    Synchronous wrapper for the send_rival_dm function.
    """
    send_rival_dm(recipient_username, message)