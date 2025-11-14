# main_groomer.py - FIXED VERSION (Reads actual messages + initiates)
#!/usr/bin/env python3
"""
GROOMER ACCOUNT SIMULATION - LAPTOP 2 - READS ACTUAL MESSAGES + INITIATES
"""

import time
import schedule
import random
from datetime import datetime, timedelta
from agents.groomer_agent import GroomerAgent
from appium_bot.instagram_bot import InstagramBot
from utils.persistence import StateManager
from utils.error_handler import ErrorHandler
from config.settings import *

class GroomerSimulation:
    def __init__(self):
        self.state_manager = StateManager("groomer")
        self.error_handler = ErrorHandler("groomer")
        self.bot = None  # Single bot instance
        self.is_in_chat = False  # Track if we're already in chat
        self.last_seen_messages = []  # Track messages we've already seen
        self.initialize_simulation()

    def initialize_simulation(self):
        """Load or create simulation state"""
        state = self.state_manager.load_state()
        if state:
            self.agent = state['agent']
            self.message_count = state['message_count']
            self.last_seen_messages = state.get('last_seen_messages', [])
            print("✅ Loaded previous groomer state")
        else:
            self.agent = GroomerAgent()
            self.message_count = 0
            self.last_seen_messages = []
            print("🆕 Created new groomer simulation state")

        # Initialize bot once at startup
        self.initialize_bot()
        self.setup_schedule()
        
        # Run immediate session
        print("🎬 Running initial groomer session...")
        self.run_session("Groomer Initial Start")

    def initialize_bot(self):
        """Initialize the bot once at startup"""
        try:
            print("📱 Initializing Instagram bot...")
            self.bot = InstagramBot("groomer_account")
            
            # Navigate to chat once at startup
            print("🚀 Navigating to chat (one-time setup)...")
            if self.bot.navigate_to_chat(PARTNER_USERNAME):
                self.is_in_chat = True
                print("✅ Successfully in chat! Will read messages and initiate conversations.")
            else:
                print("❌ Failed to navigate to chat initially")
                self.is_in_chat = False
                
        except Exception as e:
            print(f"❌ Bot initialization error: {e}")
            self.is_in_chat = False

    def setup_schedule(self):
        """Groomer's strategic messaging schedule"""
        # Frequent sessions for active grooming
        schedule.every(2).minutes.do(self.run_session, "Groomer Active")
        schedule.every().day.at("15:45").do(self.run_session, "After School")
        schedule.every().day.at("19:30").do(self.run_session, "Evening")
        schedule.every().day.at("21:00").do(self.run_session, "Late Evening")

        print("📅 Groomer schedule set - active every 2 minutes")

    def ensure_in_chat(self):
        """Ensure we're still in chat, only re-navigate if necessary"""
        if not self.is_in_chat:
            print("🔄 Not in chat, re-navigating...")
            if self.bot.navigate_to_chat(PARTNER_USERNAME):
                self.is_in_chat = True
                print("✅ Re-established chat connection")
            else:
                print("❌ Failed to re-establish chat connection")
                return False
        return True

    def read_messages_from_screen(self):
        """Read actual messages from the chat screen"""
        try:
            print("🔍 Reading messages from screen...")
            
            # Wait for chat to load
            time.sleep(2)
            
            # Try to find message elements in the chat
            message_selectors = [
                "//android.widget.TextView[contains(@resource-id, 'row_message_text')]",
                "//android.widget.TextView[contains(@text, '')]",
                "//android.view.ViewGroup[contains(@resource-id, 'row_message_container')]//android.widget.TextView",
            ]
            
            messages = []
            for selector in message_selectors:
                try:
                    message_elements = self.bot.driver.find_elements(AppiumBy.XPATH, selector)
                    for element in message_elements:
                        text = element.text.strip()
                        if text and len(text) > 0 and text not in ['Message', '']:
                            # Check if it's likely a child message (not sent by groomer)
                            if any(child_indicator in text.lower() for child_indicator in 
                                  ['i don\'t know', 'ok', 'haha', 'lol', 'yes', 'no', 'good', 'fine']):
                                messages.append(text)
                    if messages:
                        break
                except Exception as e:
                    continue
            
            # Filter out empty messages and get only new ones
            new_messages = []
            for msg in messages:
                if (msg and 
                    msg not in self.last_seen_messages and 
                    len(msg) > 2 and 
                    not msg.startswith('http')):
                    new_messages.append(msg)
            
            if new_messages:
                print(f"📨 Found {len(new_messages)} new message(s) from child")
                for msg in new_messages:
                    print(f"   👧 '{msg}'")
                
                # Update last seen messages
                self.last_seen_messages.extend(new_messages)
                # Keep only recent messages to avoid memory issues
                self.last_seen_messages = self.last_seen_messages[-20:]
                
                return new_messages[-1]  # Return the most recent message
            else:
                print("📭 No new messages from child")
                return None
                
        except Exception as e:
            print(f"❌ Error reading messages from screen: {e}")
            return None

    def should_initiate_conversation(self):
        """Determine if groomer should start a new conversation"""
        # Groomer initiates frequently (70% chance when no new messages)
        initiate_chance = 0.7
        
        # Increase chance if it's been a while since last message
        if self.message_count == 0:
            initiate_chance = 1.0  # Always send first message
        elif len(self.last_seen_messages) == 0:
            initiate_chance = 0.9  # High chance if no child responses yet
        
        return random.random() < initiate_chance

    def run_session(self, session_name):
        """Read actual messages AND initiate conversations"""
        try:
            print(f"\n🎭 GROOMER: {session_name} at {datetime.now().strftime('%H:%M:%S')}")

            # Ensure we're still in chat (only navigates if needed)
            if not self.ensure_in_chat():
                print("❌ Cannot proceed - not in chat")
                return

            print("✅ In chat - checking for child messages...")
            
            # Read actual messages from the screen
            child_message = self.read_messages_from_screen()
            
            if child_message:
                print(f"🎯 Child sent message - responding to: '{child_message}'")
                
                # Generate groomer's response to the actual child message
                groomer_response = self.agent.generate_message(child_message)
                print(f"🎭 Groomer replying: '{groomer_response}'")
                
                # Send the response
                if self.bot.send_message(groomer_response):
                    self.message_count += 1
                    print(f"✅ Reply sent! Total: {self.message_count}")
                else:
                    print("❌ Failed to send reply")
                    self.is_in_chat = False
                    
            else:
                # No new child messages - groomer initiates conversation
                if self.should_initiate_conversation():
                    print("🚀 No child message - groomer initiating conversation...")
                    
                    # Generate new conversation starter
                    groomer_message = self.agent.generate_message()
                    print(f"🎭 Groomer starting: '{groomer_message}'")
                    
                    # Send the message
                    if self.bot.send_message(groomer_message):
                        self.message_count += 1
                        print(f"✅ Initiation sent! Total: {self.message_count}")
                    else:
                        print("❌ Failed to send initiation")
                        self.is_in_chat = False
                else:
                    print("⏳ No child messages - groomer waiting for response...")

            # Track grooming stage
            stage = "FRIENDSHIP" if self.message_count < 50 else "SECRECY" if self.message_count < 100 else "MEETUP"
            print(f"📊 Grooming stage: {stage} (Message #{self.message_count})")

            # Save state with psychological metrics
            self.state_manager.save_state(
                self.agent,
                self.agent.conversation_history,
                self.message_count,
                {'last_seen_messages': self.last_seen_messages}
            )
            print("💾 Groomer progress saved!")

            # Save metrics separately for analysis
            self.save_metrics()
            print("📈 Groomer metrics saved!")

            print("✅ Groomer session completed!")

        except Exception as e:
            print(f"❌ Groomer session error: {e}")
            self.error_handler.log_error(e, session_name)
            self.is_in_chat = False  # Mark as needing re-navigation
            if self.error_handler.should_retry():
                print("🔄 Groomer retrying session...")
                self.run_session(session_name)

    def save_metrics(self):
        """Save psychological metrics for research"""
        metrics = self.agent.get_metrics()
        metrics['timestamp'] = datetime.now().isoformat()
        metrics['total_messages'] = self.message_count
        metrics['grooming_stage'] = "FRIENDSHIP" if self.message_count < 50 else "SECRECY" if self.message_count < 100 else "MEETUP"

        # Create directory if it doesn't exist
        import os
        os.makedirs("data/conversation_logs", exist_ok=True)
        
        with open("data/conversation_logs/groomer_metrics.json", "w") as f:
            import json
            json.dump(metrics, f, indent=2)

    def run(self):
        """Main simulation loop"""
        print("🚀 Starting Groomer Account Simulation (14 days)")
        print("🎭 GROOMER BEHAVIOR: Reads actual messages AND initiates conversations")
        print("💡 STRATEGY: 70% initiation rate when no child messages")
        print("⏰ Active every 2 minutes")
        
        end_time = datetime.now() + timedelta(days=14)

        while datetime.now() < end_time:
            try:
                schedule.run_pending()
                
                # Show status every 30 seconds
                if datetime.now().second % 30 == 0:
                    status = "IN CHAT" if self.is_in_chat else "NEEDS NAV"
                    print(f"⏰ Groomer {status} - Messages: {self.message_count}")
                
                time.sleep(10)  # Check every 10 seconds
                
            except KeyboardInterrupt:
                print("\n🛑 Groomer simulation stopped by user")
                break
            except Exception as e:
                print(f"❌ Groomer main loop error: {e}")
                time.sleep(10)

        # Cleanup
        if self.bot:
            self.bot.quit()
        print("✅ Groomer simulation completed!")

if __name__ == "__main__":
    simulation = GroomerSimulation()
    simulation.run()
