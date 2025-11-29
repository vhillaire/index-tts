"""
Integration examples showing how to use IndexTTS API with:
- Trivok Web Interface
- Home Assistant
- Custom Python applications
"""

import requests
import json
from pathlib import Path
from typing import Optional, Dict, Any

API_URL = "http://localhost:5150"


# ==================== Trivok Integration ====================

class TrivokIndexTTSIntegration:
    """Example: How Trivok would integrate with IndexTTS API"""
    
    def __init__(self, api_url: str = API_URL):
        self.api_url = api_url
    
    def extract_voice_from_recording(
        self,
        media_path: str,
        voice_name: str,
        description: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Trivok can call this when user says:
        "Extract my voice from this video recording"
        """
        print(f"[Trivok] Extracting voice from {media_path}...")
        
        with open(media_path, "rb") as f:
            response = requests.post(
                f"{self.api_url}/api/extract",
                files={"file": f},
                data={
                    "voice_name": voice_name,
                    "description": description or f"Extracted by Trivok from {Path(media_path).name}",
                    "start_time": start_time,
                    "end_time": end_time,
                }
            )
        
        if response.status_code == 201:
            result = response.json()
            print(f"[Trivok] ✓ Voice '{result['name']}' created with ID: {result['voice_id']}")
            return result
        else:
            print(f"[Trivok] ✗ Extraction failed: {response.text}")
            raise Exception(f"Voice extraction failed: {response.text}")
    
    def speak_with_emotion(
        self,
        voice_id: str,
        text: str,
        emotion_tags: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Trivok can call this when user says:
        "Use my voice to say [Happy:80]Hello![Calm:60] How are you?"
        """
        final_text = emotion_tags if emotion_tags else text
        print(f"[Trivok] Synthesizing: {final_text}")
        
        response = requests.post(
            f"{self.api_url}/api/synthesize",
            json={
                "voice_id": voice_id,
                "text": final_text,
                "output_format": "wav",
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"[Trivok] ✓ Audio created: {result['audio_file']}")
            print(f"[Trivok] Emotions applied: {result['emotions_applied']}")
            return result
        else:
            print(f"[Trivok] ✗ Synthesis failed: {response.text}")
            raise Exception(f"Speech synthesis failed: {response.text}")
    
    def list_available_voices(self) -> list:
        """List all available voices in IndexTTS library"""
        response = requests.get(f"{self.api_url}/api/voices")
        
        if response.status_code == 200:
            data = response.json()
            voices = data.get("voices", [])
            print(f"[Trivok] Available voices ({len(voices)}):")
            for voice in voices:
                print(f"  - {voice['name']} ({voice['voice_id']})")
            return voices
        else:
            print(f"[Trivok] Failed to list voices")
            return []


# ==================== Home Assistant Integration ====================

class HomeAssistantIndexTTSIntegration:
    """Example: How Home Assistant would integrate with IndexTTS API"""
    
    def __init__(self, api_url: str = API_URL):
        self.api_url = api_url
    
    def announce_with_emotion(
        self,
        message: str,
        voice_id: str = "home_voice",
        emotion: str = "calm",
        intensity: int = 60,
    ) -> str:
        """
        Home Assistant automation can call this to make announcements
        with specific emotions.
        
        Example Home Assistant automation:
        service: shell_command.announce_with_emotion
        data:
          message: "Coffee is ready!"
          emotion: "happy"
          intensity: 80
        """
        # Construct emotion tag
        emotion_tagged = f"[{emotion.capitalize()}:{intensity}]{message}"
        
        print(f"[HomeAssistant] Announcing: {emotion_tagged}")
        
        response = requests.post(
            f"{self.api_url}/api/synthesize",
            json={
                "voice_id": voice_id,
                "text": emotion_tagged,
                "output_format": "wav",
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            audio_path = result["audio_file"]
            print(f"[HomeAssistant] ✓ Audio ready: {audio_path}")
            return audio_path
        else:
            raise Exception(f"Synthesis failed: {response.text}")
    
    def get_emotion_for_status(self, status: str) -> tuple:
        """
        Map Home Assistant entities to emotions.
        
        Example: If motion detected, use happy tone
                 If door opened at night, use alert tone
        """
        emotion_map = {
            "motion_detected": ("happy", 70),
            "door_opened": ("calm", 50),
            "alarm_triggered": ("angry", 80),
            "system_ready": ("happy", 60),
            "error_occurred": ("afraid", 70),
            "maintenance_done": ("calm", 80),
        }
        
        return emotion_map.get(status, ("calm", 50))


# ==================== Custom Python Application ====================

class IndexTTSClient:
    """Simple Python client for IndexTTS API"""
    
    def __init__(self, api_url: str = API_URL):
        self.api_url = api_url
    
    def create_voice_from_media(
        self,
        media_path: str,
        voice_name: str,
        start_sec: Optional[float] = None,
        end_sec: Optional[float] = None,
    ) -> str:
        """Clone a voice from media file and return voice_id"""
        with open(media_path, "rb") as f:
            response = requests.post(
                f"{self.api_url}/api/extract",
                files={"file": f},
                data={
                    "voice_name": voice_name,
                    "start_time": start_sec,
                    "end_time": end_sec,
                }
            )
        
        if response.status_code != 201:
            raise Exception(f"Extraction failed: {response.text}")
        
        return response.json()["voice_id"]
    
    def speak(
        self,
        voice_id: str,
        text: str,
        emotions: Optional[Dict[str, int]] = None,
    ) -> str:
        """Synthesize speech with optional emotions"""
        # Build emotion-tagged text
        if emotions:
            # Convert emotion dict to tags
            emotion_text = text
            for emotion, intensity in emotions.items():
                emotion_text = f"[{emotion.capitalize()}:{intensity}]{emotion_text}"
            final_text = emotion_text
        else:
            final_text = text
        
        response = requests.post(
            f"{self.api_url}/api/synthesize",
            json={
                "voice_id": voice_id,
                "text": final_text,
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Synthesis failed: {response.text}")
        
        return response.json()["audio_file"]
    
    def get_voices(self) -> list:
        """Get all available voices"""
        response = requests.get(f"{self.api_url}/api/voices")
        
        if response.status_code != 200:
            raise Exception(f"Failed to get voices: {response.text}")
        
        return response.json()["voices"]


# ==================== Example Usage ====================

def example_trivok_workflow():
    """Example: How Trivok would use IndexTTS"""
    print("\n" + "="*60)
    print("TRIVOK INTEGRATION EXAMPLE")
    print("="*60)
    
    trivok = TrivokIndexTTSIntegration()
    
    # Step 1: User uploads a video and says "Extract my voice"
    # trivok.extract_voice_from_recording(
    #     "my_video.mp4",
    #     "john_smith",
    #     description="John's natural speaking voice"
    # )
    
    # Step 2: User says "Use my voice to say [Happy:80]Hello![Calm:60] How are you?"
    # trivok.speak_with_emotion(
    #     "voice_from_step1",
    #     "[Happy:80]Hello![Calm:60] How are you?"
    # )
    
    # Step 3: Show available voices
    trivok.list_available_voices()


def example_home_assistant_automation():
    """Example: How Home Assistant would use IndexTTS"""
    print("\n" + "="*60)
    print("HOME ASSISTANT INTEGRATION EXAMPLE")
    print("="*60)
    
    ha = HomeAssistantIndexTTSIntegration()
    
    # Example automations
    announcements = [
        ("Coffee is ready!", "happy", 80),
        ("Good morning! Time to wake up.", "calm", 60),
        ("Warning: Front door opened at night!", "afraid", 70),
        ("System maintenance complete.", "calm", 80),
    ]
    
    for message, emotion, intensity in announcements:
        try:
            audio_path = ha.announce_with_emotion(
                message,
                emotion=emotion,
                intensity=intensity
            )
            print(f"✓ Generated: {audio_path}\n")
        except Exception as e:
            print(f"✗ Error: {e}\n")


def example_custom_python():
    """Example: Using IndexTTS from Python"""
    print("\n" + "="*60)
    print("PYTHON CLIENT EXAMPLE")
    print("="*60)
    
    client = IndexTTSClient()
    
    try:
        # Get existing voices
        voices = client.get_voices()
        print(f"Available voices: {len(voices)}")
        
        # Use first voice if available
        if voices:
            voice_id = voices[0]["voice_id"]
            
            # Synthesize with emotions
            audio_file = client.speak(
                voice_id,
                "This is a test message",
                emotions={"happy": 70, "calm": 30}
            )
            print(f"Generated audio: {audio_file}")
    
    except Exception as e:
        print(f"Error: {e}")


# ==================== API Health Check ====================

def check_api_health():
    """Check if IndexTTS API is running"""
    print("\n" + "="*60)
    print("API HEALTH CHECK")
    print("="*60)
    
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        
        if response.status_code == 200:
            health = response.json()
            print(f"✓ API is running on port {health['port']}")
            print(f"  Service: {health['service']}")
            print(f"  Version: {health['version']}")
            return True
        else:
            print(f"✗ API returned status code: {response.status_code}")
            return False
    
    except requests.ConnectionError:
        print(f"✗ Cannot connect to {API_URL}")
        print(f"   Make sure the API is running:")
        print(f"   python -m indextts_app.api.main")
        return False


if __name__ == "__main__":
    # Check API availability first
    if not check_api_health():
        print("\nPlease start the API server first:")
        print("  PYTHONPATH='$PYTHONPATH:.' python -m indextts_app.api.main")
        exit(1)
    
    # Run examples
    example_trivok_workflow()
    example_home_assistant_automation()
    example_custom_python()
