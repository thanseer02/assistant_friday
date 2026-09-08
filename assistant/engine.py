from .intent import IntentParser
from .router import CommandRouter

class AssistantEngine:
    def __init__(self):
        """
        Initialize the AssistantEngine.
        It now acts as the orchestrator connecting the Parser and the Router.
        """
        self.parser = IntentParser()
        self.router = CommandRouter()
        
    def process(self, user_input: str) -> str:
        """
        Process the user input in two clear steps:
        1. Parse the raw string into a structured Intent.
        2. Route the Intent to execute logic and generate a response.
        """
        # Step 1: Understand what the user wants
        parsed_intent = self.parser.parse(user_input)
        
        # Step 2: Execute the action and get the result
        response = self.router.route(parsed_intent)
        
        return response
