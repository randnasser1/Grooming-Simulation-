# instagram_bot.py - SIMPLE VERSION
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
            self.account_type = account_type

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
            self.logger.info(f"✅ Appium driver initialized for {account_type}!")
            time.sleep(8)

        except Exception as e:
            self.logger.error(f"Failed to initialize {account_type}: {e}")
            raise

    def navigate_to_chat(self, target_username):
        """Simple navigation to chat with retry"""
        max_attempts = 2
        for attempt in range(max_attempts):
            try:
                self.logger.info(f"🚀 {self.account_type} navigating to chat with {target_username} (attempt {attempt + 1})")

                # Wait for app to load
                time.sleep(5)

                # Step 1: Click Messages button
                messages_selectors = [
                    (AppiumBy.ID, "com.instagram.android:id/action_bar_inbox_button"),
                    (AppiumBy.ACCESSIBILITY_ID, "No unread messages"),
                    (AppiumBy.XPATH, "//android.widget.FrameLayout[@content-desc='No unread messages']"),
                ]

                if not self.find_and_click(messages_selectors):
                    self.logger.error(f"❌ {self.account_type} could not find messages button")
                    if attempt < max_attempts - 1:
                        time.sleep(3)
                        continue
                    return False
                time.sleep(3)

                # Step 2: Click Search box in messages
                search_selectors = [
                    (AppiumBy.ID, "com.instagram.android:id/search_edit_text"),
                    (AppiumBy.ACCESSIBILITY_ID, "Search"),
                    (AppiumBy.XPATH, "//android.widget.EditText[contains(@text, 'Search')]"),
                ]

                if not self.find_and_click(search_selectors):
                    self.logger.error(f"❌ {self.account_type} could not find search box")
                    if attempt < max_attempts - 1:
                        time.sleep(3)
                        continue
                    return False
                time.sleep(2)

                # Step 3: Type the target username
                self.driver.execute_script('mobile: type', {'text': target_username})
                time.sleep(3)

                # Step 4: Click the user from search results
                user_selectors = [
                    (AppiumBy.XPATH, f"//android.widget.TextView[@text='{target_username}']"),
                    (AppiumBy.XPATH, f"//*[contains(@text, '{target_username}')]"),
                    (AppiumBy.ID, "com.instagram.android:id/row_inbox_container"),
                ]

                if not self.find_and_click(user_selectors):
                    self.logger.error(f"❌ {self.account_type} could not find user {target_username} in results")
                    if attempt < max_attempts - 1:
                        time.sleep(3)
                        continue
                    return False
                time.sleep(3)

                # Step 5: Verify we're in chat
                chat_indicators = [
                    (AppiumBy.ID, "com.instagram.android:id/row_thread_composer_edittext"),
                    (AppiumBy.ACCESSIBILITY_ID, "Voice message, press and hold to record"),
                ]

                for by, selector in chat_indicators:
                    try:
                        self.driver.find_element(by, selector)
                        self.logger.info(f"✅ {self.account_type} successfully in chat with {target_username}!")
                        return True
                    except:
                        continue

                self.logger.error(f"❌ {self.account_type} not in chat screen")
                if attempt < max_attempts - 1:
                    time.sleep(3)
                    continue
                return False

            except Exception as e:
                self.logger.error(f"❌ {self.account_type} navigation error: {e}")
                if attempt < max_attempts - 1:
                    time.sleep(3)
                    continue
                return False

    def _verify_in_chat(self):
        """Verify we're in a chat screen"""
        chat_indicators = [
            (AppiumBy.ID, "com.instagram.android:id/row_thread_composer_edittext"),
            (AppiumBy.ACCESSIBILITY_ID, "Message"),
            (AppiumBy.XPATH, "//*[contains(@text, 'Message')]"),
        ]

        for by, selector in chat_indicators:
            try:
                self.driver.find_element(by, selector)
                return True
            except:
                continue
        return False

    def find_and_click(self, selectors, timeout=10):
        """Try multiple selectors to find and click an element"""
        for by, selector in selectors:
            try:
                element = self.driver.find_element(by, selector)
                element.click()
                self.logger.info(f"✅ {self.account_type} clicked: {selector}")
                return True
            except:
                continue
        return False

    def send_message(self, text, max_attempts=3):
        """Send message"""
        for attempt in range(max_attempts):
            try:
                self.logger.info(f"💬 {self.account_type} attempt {attempt + 1} to send: {text}")

                # Find and click message input
                input_selectors = [
                    (AppiumBy.ID, "com.instagram.android:id/row_thread_composer_edittext"),
                    (AppiumBy.CLASS_NAME, "android.widget.EditText"),
                    (AppiumBy.XPATH, "//android.widget.EditText[contains(@text, 'Message')]"),
                ]

                if not self.find_and_click(input_selectors):
                    self.logger.error(f"❌ {self.account_type} could not find message input")
                    continue
                time.sleep(1)

                # Type message
                self.driver.execute_script('mobile: type', {'text': text})
                time.sleep(1)

                # Send message
                send_selectors = [
                    (AppiumBy.ACCESSIBILITY_ID, "Send"),
                    (AppiumBy.ID, "com.instagram.android:id/row_thread_composer_button_send"),
                ]

                if self.find_and_click(send_selectors):
                    self.logger.info(f"✅ {self.account_type} sent: {text}")
                    return True
                else:
                    # Fallback: press enter
                    self.driver.press_keycode(66)
                    self.logger.info(f"✅ {self.account_type} sent via Enter: {text}")
                    return True

            except Exception as e:
                self.logger.warning(f"❌ {self.account_type} attempt {attempt + 1} failed: {e}")
                time.sleep(2)

        return False

    def quit(self):
        if self.driver:
            self.driver.quit()
            self.logger.info(f"✅ {self.account_type} bot quit")

# Test
if __name__ == "__main__":
    bot = InstagramBot("child_account")
    try:
        if bot.navigate_to_chat("test_username"):
            bot.send_message("Test message from simple bot!")
    finally:
        bot.quit()
