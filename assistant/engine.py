from .intent import IntentParser
from .router import CommandRouter
from ai.local_model import OllamaModel

class AssistantEngine:
    def __init__(self):
        """
        Initialize the AssistantEngine.
        It now acts as the orchestrator connecting the AI Parser and the Router.
        """
        # Instantiate the local LLM and inject it into the parser
        # You can change "llama3" to "mistral" or any other locally installed model
        self.llm = OllamaModel(model_name="llama3")
        self.parser = IntentParser(llm=self.llm)
        self.router = CommandRouter()
        
    def process(self, user_input: str) -> str:
        """
        Process the user input in two clear steps:
        1. AI Parser converts the raw string into a structured Intent.
        2. Router safely executes the predefined logic.
        """
        # Step 1: Use AI to understand what the user wants
        parsed_intent = self.parser.parse(user_input)
        
        # Step 2: Safely execute the action
        response = self.router.route(parsed_intent)
        
        return response
