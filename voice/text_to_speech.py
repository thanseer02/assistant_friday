import platform
import subprocess

class TextToSpeech:
    """
    Handles local Text-to-Speech (TTS) conversion.
    This acts as an output adapter and is completely decoupled from the Assistant Engine.
    """
    def __init__(self):
        self.os_name = platform.system()

    def speak(self, text: str):
        if not text:
            return
            
        try:
            # We use native OS commands to avoid forcing the user to install third-party 
            # libraries like pyttsx3, keeping the project lightweight.
            if self.os_name == "Darwin":
                # macOS built-in 'say' command
                subprocess.run(["say", text], check=False)
                
            elif self.os_name == "Windows":
                # Windows built-in PowerShell SpeechSynthesizer API
                # Clean up single quotes to prevent PowerShell syntax errors
                clean_text = text.replace("'", "")
                ps_cmd = f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{clean_text}')"
                # Run the PowerShell command silently
                subprocess.run(["powershell", "-Command", ps_cmd], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
            else:
                # Fallback for Linux or unknown OS
                print(f"[Voice Fallback Output]: {text}")
                
        except Exception as e:
            print(f"[Voice Error] Could not play audio: {str(e)}")
