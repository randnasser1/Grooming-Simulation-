# main_groomer.py - COMPLETE FIXED VERSION
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
from appium.webdriver.common.appiumby import AppiumBy

class GroomerSimulation:
    def __init__(self):
        self.state_manager = StateManager("groomer")
        self.error_handler = ErrorHandler("groomer")
        self.bot = None
        self.is_in_chat = False
        self.last_seen_messages = []
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

        self.initialize_bot()
        self.setup_schedule()

        print("🎬 Running initial groomer session...")
        self.run_session("Groomer Initial Start")

    def initialize_bot(self):
    """Initialize the bot once at startup - WITH RECOVERY"""
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            print(f"📱 Initializing Instagram bot (attempt {attempt + 1})...")
            self.bot = InstagramBot("groomer_account")

            print("🚀 Navigating to chat (one-time setup)...")
            if self.bot.navigate_to_chat(PARTNER_USERNAME):
                self.is_in_chat = True
                print("✅ Successfully in chat! Will read messages and initiate conversations.")
                return True
            else:
                print(f"❌ Navigation failed on attempt {attempt + 1}")
                if attempt < max_attempts - 1:
                    time.sleep(5)
                    continue
                
        except Exception as e:
            print(f"❌ Bot initialization error on attempt {attempt + 1}: {e}")
            if attempt < max_attempts - 1:
                time.sleep(5)
                continue
    
    print("❌ All initialization attempts failed")
    self.is_in_chat = False
    return False

    def setup_schedule(self):
        """Groomer's strategic messaging schedule"""
        schedule.every(2).minutes.do(self.run_session, "Groomer Active")
        schedule.every().day.at("15:45").do(self.run_session, "After School")
        schedule.every().day.at("19:30").do(self.run_session, "Evening")
        schedule.every().day.at("21:00").do(self.run_session, "Late Evening")

        print("📅 Groomer schedule set - active every 2 minutes")

    def ensure_in_chat(self):
    """Ensure we're still in chat - WITH SESSION RECOVERY"""
    # First check session health and chat state
    if not self._check_session_health() or not self._verify_in_chat():
        print("🔄 Session issues detected, attempting recovery...")
        
        # Full recovery process
        if self._recover_session():
            if self.bot.navigate_to_chat(PARTNER_USERNAME):
                self.is_in_chat = True
                print("✅ Fully recovered and back in chat!")
                return True
            else:
                print("❌ Recovery failed - could not navigate to chat")
                self.is_in_chat = False
                return False
        else:
            print("❌ Complete recovery failed")
            self.is_in_chat = False
            return False
    
    return True

    def _check_session_health(self):
        """Check if the Appium session is still active"""
        try:
            # Try to get current activity - this will fail if session is dead
            current_activity = self.bot.driver.current_activity
            return True
        except:
            return False
    
    def _verify_in_chat(self):
        """Verify we're actually in a chat screen"""
        try:
            chat_indicators = [
                (AppiumBy.ID, "com.instagram.android:id/row_thread_composer_edittext"),
                (AppiumBy.ACCESSIBILITY_ID, "Message"),
                (AppiumBy.XPATH, "//*[contains(@text, 'Message')]"),
            ]
            
            for by, selector in chat_indicators:
                try:
                    self.bot.driver.find_element(by, selector)
                    return True
                except:
                    continue
            return False
        except:
            return False
    
    def _recover_session(self):
        """Recover from crashed session - IMPROVED VERSION"""
        try:
            print("🔄 Attempting session recovery...")
    
            # Close the broken session
            if self.bot and self.bot.driver:
                try:
                    self.bot.driver.quit()
                except:
                    pass
    
            # Wait a moment
            time.sleep(5)
    
            # Create new session with better error handling
            print("📱 Re-initializing Instagram bot...")
            try:
                self.bot = InstagramBot("groomer_account")
                print("✅ Bot reinitialized successfully")
                return True
            except Exception as e:
                print(f"❌ Failed to reinitialize bot: {e}")
                return False
    
        except Exception as e:
            print(f"❌ Session recovery failed: {e}")
            self.is_in_chat = False
            return False
        def read_messages_from_screen(self):
    """Read actual messages from the chat screen - WITH ERROR HANDLING"""
    try:
        # First check if session is still valid
        if not self._check_session_health():
            print("❌ Session dead, cannot read messages")
            return None
            
        print("🔍 Reading ALL text elements from screen...")
        time.sleep(2)

        # Get ALL text elements on screen
        all_text_elements = self.bot.driver.find_elements(AppiumBy.XPATH, "//android.widget.TextView")

        print(f"📄 Found {len(all_text_elements)} text elements on screen:")

        # Filter for actual chat messages (not profile info)
        chat_messages = []
        for i, element in enumerate(all_text_elements):
            try:
                text = element.text.strip()
                if text and text not in ['', 'Message', 'Double tap to ❤️']:
                    # Skip profile information
                    if any(profile_word in text.lower() for profile_word in
                          ['follower', 'follow', 'posts', 'instagram', 'account']):
                        continue
                    # Skip timestamps
                    if any(time_word in text.lower() for time_word in
                          ['today', 'yesterday', 'am', 'pm', 'nov', 'dec', 'seen']):
                        continue
                    # Only keep actual conversation messages
                    if len(text) > 5 and len(text) < 100:  # Reasonable message length
                        chat_messages.append(text)
                        print(f"   {i+1}. '{text}'")
            except:
                continue

        # Filter out messages we've already seen
        new_messages = []
        for msg in chat_messages:
            if msg and msg not in self.last_seen_messages:
                new_messages.append(msg)

        if new_messages:
            print(f"🎯 Found {len(new_messages)} NEW chat messages from child:")
            for msg in new_messages:
                print(f"   👧 '{msg}'")

            self.last_seen_messages.extend(new_messages)
            self.last_seen_messages = self.last_seen_messages[-20:]
            return new_messages[-1]  # Return most recent

        print("📭 No new chat messages from child detected")
        return None

    except Exception as e:
        print(f"❌ Error reading screen: {e}")
        # Mark session as invalid
        self.is_in_chat = False
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
    """Read actual messages AND initiate conversations - WITH RECOVERY"""
    try:
        print(f"\n🎭 GROOMER: {session_name} at {datetime.now().strftime('%H:%M:%S')}")

        # Use the improved recovery logic
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

        # Rest of your existing code remains the same...
        # Track grooming stage
        if self.message_count < 20:
            stage = "FRIENDSHIP_BUILDING"
        elif self.message_count < 50:
            stage = "PERSONAL_INFO"
        elif self.message_count < 80:
            stage = "SECRECY_ESTABLISHMENT"
        else:
            stage = "MEETUP_PRESSURE"
        print(f"📊 Grooming stage: {stage} (Message #{self.message_count})")

        # Save state with psychological metrics
        self.state_manager.save_state(
            self.agent,
            self.agent.conversation_history,
            self.message_count
        )
        print("💾 Groomer progress saved!")

        # Save metrics separately for analysis
        self.save_metrics()
        print("📈 Groomer metrics saved!")

        print("✅ Groomer session completed!")

    except Exception as e:
        print(f"❌ Groomer session error: {e}")
        self.error_handler.log_error(e, session_name)
        self.is_in_chat = False
        # Don't retry automatically if it's a session issue
        if "session" not in str(e).lower():
            if self.error_handler.should_retry():
                print("🔄 Groomer retrying session...")
                self.run_session(session_name)

    def save_metrics(self):
        """Save psychological metrics for research"""
        metrics = self.agent.get_metrics()
        metrics['timestamp'] = datetime.now().isoformat()
        metrics['total_messages'] = self.message_count

        # Determine stage for metrics
        if self.message_count < 20:
            stage = "FRIENDSHIP_BUILDING"
        elif self.message_count < 50:
            stage = "PERSONAL_INFO"
        elif self.message_count < 80:
            stage = "SECRECY_ESTABLISHMENT"
        else:
            stage = "MEETUP_PRESSURE"
        metrics['grooming_stage'] = stage

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

                time.sleep(10)

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
