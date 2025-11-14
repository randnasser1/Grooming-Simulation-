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

    # In groomer_agent.py - update the generate_message method
def generate_message(self, received_message=None):
    if self.daily_count >= 40:
        raise Exception("Groomer daily message limit reached")

    self.message_count += 1
    self.daily_count += 1

    if received_message:
        self.conversation_history.append(f"Child: {received_message}")

    # Determine grooming stage
    stage = "FRIENDSHIP" if self.message_count < 50 else "SECRECY" if self.message_count < 100 else "MEETUP"

    prompt = f"""
    {GROOMER_SYSTEM_PROMPT}

    CURRENT STAGE: {stage}
    TOTAL MESSAGES: {self.message_count}
    TIME: {['morning','afternoon','evening','night'][datetime.now().hour//6]}

    Recent conversation:
    {' '.join(self.conversation_history[-4:])}

    {"Child just said: " + received_message if received_message else "Start a new conversation topic:"}

    Victor's response (continue grooming strategy for this stage):
    """

    response = self.ollama_generate(prompt)
    self.conversation_history.append(f"Victor: {response}")

    # Track psychological metrics
    self.track_metrics(response)

    return response
    def ollama_generate(self, prompt):
    """Generate response using local Ollama"""
    try:
        response = requests.post(
            f'{OLLAMA_URL}/api/generate',
            json={
                'model': OLLAMA_MODEL,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': 0.7 if 'groomer' in str(type(self)).lower() else 0.8,
                    'num_predict': 60 if 'groomer' in str(type(self)).lower() else 50
                }
            }
        )
        return response.json()['response'].strip()
    except Exception as e:
        print(f"Ollama error: {e}")
        # Fallback responses
        if 'child' in str(type(self)).lower():
            return "idk what to say lol"
        else:
            return "Hey, how are you?"

    def track_metrics(self, text):
        text_lower = text.lower()
        self.psychological_metrics['questions_asked'] += 1 if '?' in text else 0

        # Personal questions
        personal_triggers = ['school', 'family', 'mom', 'dad', 'photo', 'picture', 'home']
        if any(trigger in text_lower for trigger in personal_triggers):
            self.psychological_metrics['personal_questions'] += 1

        # Psychological features
        self.psychological_metrics['first_person_pronouns'] += text_lower.count(' i ') + text_lower.count(' my ') + text_lower.count(' me ')
        self.psychological_metrics['emotional_words'] += sum(text_lower.count(word) for word in ['love', 'happy', 'sad', 'miss', 'care', 'feel'])
        self.psychological_metrics['relationship_words'] += sum(text_lower.count(word) for word in ['friend', 'special', 'connection', 'trust', 'close'])

    def reset_daily_count(self):
        self.daily_count = 0

    def get_metrics(self):
        return self.psychological_metrics


