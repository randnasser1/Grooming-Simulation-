# instagram_bot_precise.py
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
import time
import random
import json
import logging

class InstagramBot:
    def __init__(self, account_type):
        try:
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger(__name__)

            # Load capabilities
            with open('appium_bot/capabilities.json', 'r') as f:
                caps_data = json.load(f)
            caps = caps_data[account_type]

            options = UiAutomator2Options()
            options.platform_name = caps.get("platformName", "Android")
            options.platform_version = caps.get("platformVersion", "13")
            options.device_name = caps.get("deviceName", "Android Emulator")
            options.app_package = caps.get("appPackage", "com.instagram.android")
            options.app_activity = caps.get("appActivity", "com.instagram.android.activity.MainTabActivity")
            options.automation_name = caps.get("automationName", "UiAutomator2")
            options.no_reset = caps.get("noReset", True)

            self.driver = webdriver.Remote('http://127.0.0.1:4723', options=options)
            self.account_type = account_type
            self.logger.info("✅ Appium driver initialized!")
            time.sleep(8)

        except Exception as e:
            self.logger.error(f"Failed to initialize: {e}")
            raise

    def find_and_click(self, selectors, timeout=10):
        """Try multiple selectors to find and click an element"""
        for by, selector in selectors:
            try:
                element = self.driver.find_element(by, selector)
                element.click()
                self.logger.info(f"✅ Clicked: {selector}")
                return True
            except:
                continue
        return False

    def navigate_to_chat(self, target_username):
        """Navigate to chat using REAL element IDs from your exploration"""
        try:
            self.logger.info(f"🚀 Navigating to chat with {target_username}")

            # Step 1: Click Messages button (from home screen)
            messages_selectors = [
                # Use the exact resource ID from your exploration
                (AppiumBy.ID, "com.instagram.android:id/action_bar_inbox_button"),
                # Or the accessibility ID
                (AppiumBy.ACCESSIBILITY_ID, "No unread messages"),
                # Or the bottom nav messages
                (AppiumBy.XPATH, "//android.widget.FrameLayout[@content-desc='No unread messages']"),
            ]

            if not self.find_and_click(messages_selectors):
                self.logger.error("❌ Could not find messages button")
                return False
            time.sleep(3)

            # Step 2: Click Search box in messages
            search_selectors = [
                (AppiumBy.ID, "com.instagram.android:id/search_edit_text"),
                (AppiumBy.ACCESSIBILITY_ID, "Search"),
                (AppiumBy.XPATH, "//android.widget.EditText[contains(@text, 'Search')]"),
            ]

            if not self.find_and_click(search_selectors):
                self.logger.error("❌ Could not find search box")
                return False
            time.sleep(2)

            # Step 3: Type username
            self.driver.execute_script('mobile: type', {'text': target_username})
            time.sleep(3)

            # Step 4: Click the user from search results
            user_selectors = [
                # Look for the username in the results
                (AppiumBy.XPATH, f"//android.widget.TextView[@text='{target_username}']"),
                (AppiumBy.XPATH, f"//*[contains(@text, '{target_username}')]"),
                # Or tap the user container
                (AppiumBy.ID, "com.instagram.android:id/row_inbox_container"),
            ]

            if not self.find_and_click(user_selectors):
                self.logger.error("❌ Could not find user in results")
                return False
            time.sleep(3)

            # Step 5: We should now be in the chat - verify
            chat_indicators = [
                (AppiumBy.ID, "com.instagram.android:id/row_thread_composer_edittext"),
                (AppiumBy.ACCESSIBILITY_ID, "Voice message, press and hold to record"),
            ]

            for by, selector in chat_indicators:
                try:
                    self.driver.find_element(by, selector)
                    self.logger.info("✅ Successfully in chat!")
                    return True
                except:
                    continue

            self.logger.error("❌ Not in chat screen")
            return False

        except Exception as e:
            self.logger.error(f"Navigation error: {e}")
            return False

    def send_message(self, text, max_attempts=3):
        """Send message using the exact message input element"""
        for attempt in range(max_attempts):
            try:
                self.logger.info(f"Attempt {attempt + 1} to send: {text}")

                # Find and click the message input
                input_selectors = [
                    (AppiumBy.ID, "com.instagram.android:id/row_thread_composer_edittext"),
                    (AppiumBy.CLASS_NAME, "android.widget.EditText"),
                    (AppiumBy.XPATH, "//android.widget.EditText[contains(@text, 'Message')]"),
                ]

                if not self.find_and_click(input_selectors):
                    self.logger.error("❌ Could not find message input")
                    continue
                time.sleep(1)

                # Type the message
                self.driver.execute_script('mobile: type', {'text': text})
                time.sleep(random.uniform(1, 2))

                # Find and click send button
                send_selectors = [
                    # The send button is usually near the message input
                    (AppiumBy.ACCESSIBILITY_ID, "Send"),
                    (AppiumBy.XPATH, "//android.widget.Button[contains(@content-desc, 'Send')]"),
                    # Sometimes it's the paper plane icon in the input area
                    (AppiumBy.ID, "com.instagram.android:id/row_thread_composer_button_send"),
                ]

                if self.find_and_click(send_selectors):
                    self.logger.info(f"✅ {self.account_type} sent: {text}")
                    return True
                else:
                    # If no send button found, try pressing enter
                    self.driver.press_keycode(66)  # Enter key
                    self.logger.info(f"✅ {self.account_type} sent via Enter: {text}")
                    return True

            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(2)

        return False

    def quick_send(self, text):
        """Quick message sending for simple texts"""
        try:
            # Directly target the message input
            message_input = self.driver.find_element(
                AppiumBy.ID, "com.instagram.android:id/row_thread_composer_edittext"
            )
            message_input.click()
            time.sleep(0.5)
            message_input.send_keys(text)
            time.sleep(0.5)

            # Try to find and click send button
            try:
                send_btn = self.driver.find_element(
                    AppiumBy.ID, "com.instagram.android:id/row_thread_composer_button_send"
                )
                send_btn.click()
            except:
                # Fallback: press enter
                self.driver.press_keycode(66)

            self.logger.info(f"✅ Quick sent: {text}")

        except Exception as e:
            self.logger.error(f"Quick send failed: {e}")

    def quit(self):
        if self.driver:
            self.driver.quit()

# Test it
if __name__ == "__main__":
    bot = InstagramBot("child_account")
    try:
        if bot.navigate_to_chat("victorhalloway12"):
            bot.send_message("Hello from the precise bot! 🎯")
            time.sleep(2)
            bot.quick_send("This should work perfectly! 🚀")
    finally:
        bot.quit()
