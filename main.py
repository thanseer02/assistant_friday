import sys
from assistant.engine import AssistantEngine
from voice.text_to_speech import TextToSpeech
from voice.speech_to_text import SpeechToText

def main():
    print("========================================")
    print("  Welcome to the Local AI Assistant!    ")
    print("========================================")
    
    # Check if voice is enabled via command line argument (disabled by default)
    voice_enabled = "--voice" in sys.argv
    
    # Instantiate Voice Adapters (Input and Output)
    tts = TextToSpeech() if voice_enabled else None
    stt = SpeechToText() if voice_enabled else None
    
    if voice_enabled:
        print("[System] Voice mode enabled. Using local microphone and speakers.\n")
    else:
        print("Type 'help' to see what I can do.")
        print("Type 'exit' or 'quit' to close the app.")
        print("Run with 'python main.py --voice' to enable voice capabilities.\n")
    
    # The Core Engine is completely unaware of voice vs text
    engine = AssistantEngine()
    
    while True:
        try:
            # ==============================
            # 1. INPUT LAYER
            # ==============================
            if voice_enabled and stt and stt.is_available:
                user_input = stt.listen()
                if not user_input:
                    continue
                print(f"You (Voice): {user_input}")
            else:
                user_input = input("You: ")
                if not user_input.strip():
                    continue
            
            # ==============================
            # 2. PROCESSING LAYER
            # ==============================
            # The engine treats speech exactly the same as typed text
            response = engine.process(user_input)
            print(f"Assistant: {response}\n")
            
            # ==============================
            # 3. OUTPUT LAYER
            # ==============================
            if voice_enabled and tts:
                tts.speak(response)
            
            # Check for exit
            if user_input.strip().lower() in ["exit", "quit", "goodbye"]:
                break
                
        except (KeyboardInterrupt, EOFError):
            print("\nAssistant: Goodbye! Have a great day!\n")
            break

if __name__ == "__main__":
    main()
