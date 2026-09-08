import datetime
import os
from .intent import Intent, ParsedIntent

class CommandRouter:
    def route(self, parsed_intent: ParsedIntent) -> str:
        """
        Takes a structured intent, executes the corresponding action, 
        and returns a response string.
        """
        intent = parsed_intent.intent
        entities = parsed_intent.entities
        
        if intent == Intent.GREETING:
            return "Hello! How can I help you today?"
            
        if intent == Intent.HELP:
            return (
                "Available commands (try typing these naturally):\n"
                "  - hello / hi\n"
                "  - what time is it\n"
                "  - tell me the date\n"
                "  - calculate [expression] (e.g., calculate 25 * 10)\n"
                "  - open [app] (e.g., open calculator)\n"
                "  - create a folder called [name]\n"
                "  - help\n"
                "  - exit / quit"
            )
            
        if intent == Intent.EXIT:
            return "Goodbye! Have a great day!"
            
        if intent == Intent.GET_TIME:
            now = datetime.datetime.now()
            return f"The current time is {now.strftime('%I:%M %p')}."
            
        if intent == Intent.GET_DATE:
            today = datetime.date.today()
            return f"Today's date is {today.strftime('%B %d, %Y')}."
            
        if intent == Intent.CALCULATE:
            expression = entities.get("expression", "")
            # Basic validation to safely use eval() for simple math
            allowed_chars = set("0123456789+-*/. ")
            if expression and set(expression).issubset(allowed_chars):
                try:
                    result = eval(expression)
                    return f"The result is {result}."
                except Exception:
                    return "I couldn't calculate that. Please provide a valid math expression."
            else:
                return "Please provide a basic math expression using numbers and operators (+, -, *, /)."
                
        if intent == Intent.OPEN_APP:
            app_name = entities.get("app_name", "")
            if not app_name:
                return "Please specify an app to open."
            # Since this should work on both Windows and Mac eventually, we'll just simulate it for now.
            return f"[Simulated Action Executed] Opening {app_name}..."
            
        if intent == Intent.CREATE_FOLDER:
            folder_name = entities.get("folder_name", "")
            if not folder_name:
                return "Please specify a folder name."
            try:
                # Creates the folder in the current working directory safely
                os.makedirs(folder_name, exist_ok=True)
                return f"[Action Executed] Created folder '{folder_name}' successfully."
            except Exception as e:
                return f"Failed to create folder: {str(e)}"
            
        # Fallback for Intent.UNKNOWN
        return f"I don't understand '{parsed_intent.raw_input}'. Type 'help' for examples."
