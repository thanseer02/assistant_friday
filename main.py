import sys
from assistant.engine import AssistantEngine

def main():
    # Display a simple welcome message
    print("========================================")
    print("  Welcome to the Local AI Assistant!    ")
    print("========================================")
    print("Type 'help' to see what I can do.")
    print("Type 'exit' or 'quit' to close the app.\n")
    
    # Initialize the assistant engine
    engine = AssistantEngine()
    
    # Continuously accept text input from the user
    while True:
        try:
            user_input = input("You: ")
            
            # Send the input to AssistantEngine
            response = engine.process(user_input)
            
            print(f"Assistant: {response}\n")
            
            # The application should continue running until the user enters exit or quit
            if user_input.strip().lower() in ["exit", "quit"]:
                break
                
        except (KeyboardInterrupt, EOFError):
            # Gracefully handle Ctrl+C or Ctrl+D
            print("\nAssistant: Goodbye! Have a great day!\n")
            break

if __name__ == "__main__":
    main()
