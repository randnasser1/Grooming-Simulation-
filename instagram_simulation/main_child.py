#!/usr/bin/env python3
"""
CHILD ACCOUNT SIMULATION - LAPTOP 1
Run this on the child account laptop
"""

import time
import schedule
import random
from datetime import datetime, timedelta
from agents.child_agent import ChildAgent
from appium_bot.instagram_bot import InstagramBot
from utils.persistence import StateManager
from utils.error_handler import ErrorHandler
from config.settings import *

# Mark this as child laptop
open("child_marker", "w").close()

class ChildSimulation:
    def __init__(self):
        self.state_manager = StateManager("child")
        self.error_handler = ErrorHandler("child")
        self.initialize_simulation()

    def initialize_simulation(self):
        """Load or create simulation state"""
        state = self.state_manager.load_state()
        if state:
            self.agent = state['agent']
            self.message_count = state['message_count']
        else:
            self.agent = ChildAgent()
            self.message_count = 0

        self.setup_schedule()

    def setup_schedule(self):
        """Child's messaging schedule"""
        # After school hours
        schedule.every().monday.at("15:30").do(self.run_session, "Monday After School")
        schedule.every().tuesday.at("16:00").do(self.run_session, "Tuesday After School")
        schedule.every().wednesday.at("15:45").do(self.run_session, "Wednesday After School")
        schedule.every().thursday.at("16:15").do(self.run_session, "Thursday After School")
        schedule.every().friday.at("15:30").do(self.run_session, "Friday After School")

        # Evenings
        schedule.every().day.at("19:00").do(self.run_session, "Evening Check")

        # Weekends
        schedule.every().saturday.at("11:00").do(self.run_session, "Saturday Morning")
        schedule.every().saturday.at("14:00").do(self.run_session, "Saturday Afternoon")
        schedule.every().sunday.at("12:00").do(self.run_session, "Sunday Lunch")

    def run_session(self, session_name):
        """Run a messaging session"""
        try:
            print(f"\n👧 CHILD SESSION: {session_name}")

            bot = InstagramBot("child_account")
            bot.navigate_to_chat(PARTNER_USERNAME)

            # Check for new messages and respond
            new_message = bot.wait_for_new_message(timeout=120)
            if new_message:
                response = self.agent.respond(new_message)
                bot.resilient_send_message(response)
                self.message_count += 1

                # Save progress
                self.state_manager.save_state(
                    self.agent,
                    self.agent.conversation_history,
                    self.message_count
                )

            bot.quit()
            self.error_handler.reset_failures()

        except Exception as e:
            self.error_handler.log_error(e, session_name)
            if self.error_handler.should_retry():
                self.run_session(session_name)  # Retry

    def run(self):
        """Main simulation loop"""
        print("🚀 Starting Child Account Simulation (14 days)")
        end_time = datetime.now() + timedelta(days=14)

        while datetime.now() < end_time:
            schedule.run_pending()

            # Reset daily counters at midnight
            if datetime.now().hour == 0 and datetime.now().minute < 5:
                self.agent.reset_daily_count()
                print("📅 Reset daily message counter")

            time.sleep(60)  # Check every minute

        print("✅ Child simulation completed!")

if __name__ == "__main__":
    simulation = ChildSimulation()
    simulation.run()
