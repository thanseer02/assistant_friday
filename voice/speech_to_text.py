class SpeechToText:
    """
    Handles local Speech-to-Text (STT) conversion.
    This acts as an input adapter and is completely decoupled from the Assistant Engine.
    """
    def __init__(self):
        self.is_available = False
        
        # We try to load the SpeechRecognition and PyAudio libraries dynamically.
        # If they aren't installed, the application won't crash; it simply disables voice input.
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            self.is_available = True
        except ImportError:
            print("[System Warning] 'SpeechRecognition' or 'PyAudio' missing. Microphone input disabled.")
            print("To enable, run: pip install SpeechRecognition pyaudio pocketsphinx")

    def listen(self) -> str:
        """
        Listens to the microphone and returns the transcribed text.
        """
        if not self.is_available:
            return ""
            
        import speech_recognition as sr
        with self.microphone as source:
            print("\n[🎙️ Listening... Speak now]")
            # Automatically adapt to background noise
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            try:
                # Listen for up to 10 seconds of speech
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
                # We use recognize_sphinx() because it runs 100% locally and offline.
                # recognize_google() is easier but sends audio to the cloud, violating requirements.
                text = self.recognizer.recognize_sphinx(audio)
                return text
                
            except sr.WaitTimeoutError:
                return ""
            except sr.UnknownValueError:
                print("[System] Could not understand audio.")
                return ""
            except Exception as e:
                print(f"[System] Voice Input Error: {e}")
                return ""
