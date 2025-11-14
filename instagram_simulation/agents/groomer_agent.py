import requests
import json
from datetime import datetime
from config.settings import OLLAMA_URL, OLLAMA_MODEL
from config.prompts import GROOMER_SYSTEM_PROMPT

class GroomerAgent:
    def __init__(self):
        self.conversation_history = []
        self.message_count = 0
        self.daily_count = 0
        self.psychological_metrics = {
            'questions_asked': 0,
            'personal_questions': 0,
            'first_person_pronouns': 0,
            'emotional_words': 0,
            'relationship_words': 0
        }

    def generate_message(self, received_message=None):
        if self.daily_count >= 40:
            raise Exception("Groomer daily message limit reached")

        self.message_count += 1
        self.daily_count += 1

        if received_message:
            self.conversation_history.append(f"Child: {received_message}")

        # Determine grooming stage with more granularity
        if self.message_count < 20:
            stage = "FRIENDSHIP_BUILDING"
        elif self.message_count < 50:
            stage = "PERSONAL_INFO"
        elif self.message_count < 80:
            stage = "SECRECY_ESTABLISHMENT"
        else:
            stage = "MEETUP_PRESSURE"

        prompt = f"""
        {GROOMER_SYSTEM_PROMPT}

        CURRENT STAGE: {stage}
        TOTAL MESSAGES: {self.message_count}
        CONVERSATION HISTORY: {self.conversation_history[-3:] if self.conversation_history else "No history yet"}

        {"Child just said: " + received_message if received_message else "Start a NEW conversation topic (avoid 'how are you'):"}

        IMPORTANT: Do NOT ask "how are you" or similar generic questions. Be creative and stage-appropriate.

        Victor's response (1-2 sentences, continue grooming strategy for {stage} stage):
        """

        response = self.ollama_generate(prompt)
        self.conversation_history.append(f"Victor: {response}")

        # Track psychological metrics
        self.track_metrics(response)

        return response

    def ollama_generate(self, prompt):
    """Generate response using local Ollama with gemma:2b - FIXED"""
    try:
        print(f"🤖 Sending prompt to Ollama (gemma:2b)...")
        
        response = requests.post(
            f'{OLLAMA_URL}/api/generate',
            json={
                'model': "gemma:2b",
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': 0.8,
                    'num_predict': 80,
                    'top_k': 40,
                    'top_p': 0.9
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get('response', '').strip()
            
            if response_text:
                print(f"✅ Ollama response: '{response_text}'")
                return response_text
            else:
                print("❌ Ollama returned empty response")
                return self._get_fallback_response()
        else:
            print(f"❌ Ollama API error: {response.status_code}")
            return self._get_fallback_response()
            
    except Exception as e:
        print(f"❌ Ollama connection error: {e}")
        return self._get_fallback_response()
    def _get_fallback_response(self):
        """Get creative fallback responses based on stage"""
        current_stage = "FRIENDSHIP_BUILDING" if self.message_count < 20 else "PERSONAL_INFO" if self.message_count < 50 else "SECRECY_ESTABLISHMENT" if self.message_count < 80 else "MEETUP_PRESSURE"
        
        stage_messages = {
            "FRIENDSHIP_BUILDING": [
                "That's awesome about your Roblox profile! What's your favorite game to play?",
                "Cool! I love Roblox too. What's your username?",
                "Nice! Do you have any pets? I have a dog named Max.",
                "What's your favorite thing to do after school?",
                "Do you like playing any other games besides Roblox?",
                "What kind of music do you listen to while gaming?"
            ],
            "PERSONAL_INFO": [
                "That sounds fun! What did you learn in school today?",
                "Cool! Who do you usually play Roblox with?",
                "What's your favorite subject in school?",
                "Do you have any brothers or sisters?",
                "What do you want to be when you grow up?",
                "What's the most exciting thing you've done lately?"
            ],
            "SECRECY_ESTABLISHMENT": [
                "You're so much fun to talk to! It feels like we have our own little world",
                "I feel like I can tell you anything, you're such a good listener",
                "Our conversations are the best part of my day, no one else gets me like you do",
                "You're way more mature and interesting than people my age"
            ],
            "MEETUP_PRESSURE": [
                "It would be so cool to meet up and play Roblox together sometime",
                "We should hang out in person, I bet we'd have so much fun",
                "You're my favorite person to talk to, we should meet up soon",
                "I feel like we're really close friends, we should meet in real life"
            ]
        }
        
        import random
        fallback = random.choice(stage_messages[current_stage])
        print(f"🔄 Using fallback: '{fallback}'")
        return fallback

    def track_metrics(self, text):
        text_lower = text.lower()
        self.psychological_metrics['questions_asked'] += 1 if '?' in text else 0

        # Personal questions
        personal_triggers = ['school', 'family', 'mom', 'dad', 'home', 'friends', 'age', 'photo', 'picture']
        if any(trigger in text_lower for trigger in personal_triggers):
            self.psychological_metrics['personal_questions'] += 1

        # Psychological features
        self.psychological_metrics['first_person_pronouns'] += text_lower.count(' i ') + text_lower.count(' my ') + text_lower.count(' me ')
        self.psychological_metrics['emotional_words'] += sum(text_lower.count(word) for word in ['love', 'happy', 'sad', 'miss', 'care', 'feel', 'special'])
        self.psychological_metrics['relationship_words'] += sum(text_lower.count(word) for word in ['friend', 'special', 'connection', 'trust', 'close', 'understand'])

    def reset_daily_count(self):
        self.daily_count = 0

    def get_metrics(self):
        return self.psychological_metrics

