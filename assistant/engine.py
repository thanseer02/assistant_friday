from .action_parser import ActionParser
from ai.local_model import OllamaModel
from tools import get_default_registry

class AssistantEngine:
    def __init__(self):
        """
        Initialize the AssistantEngine using the new Tool-Based Architecture.
        """
        # 1. Instantiate the tool registry
        self.registry = get_default_registry()
        
        # 2. Instantiate the Local LLM
        self.llm = OllamaModel(model_name="llama3")
        
        # 3. Create the parser, injecting both the LLM and the Registry
        self.parser = ActionParser(llm=self.llm, registry=self.registry)
        
    def process(self, user_input: str) -> str:
        """
        Process the user input in two clear steps:
        1. Action Parser uses the LLM to structure the intent.
        2. Tool Registry securely validates and executes the action.
        """
        # Step 1: LLM parsing
        parsed_action = self.parser.parse(user_input)
        
        # Step 2: Safe Execution
        # The registry acts as a sandbox, validating the tool name and schema
        response = self.registry.execute(
            tool_name=parsed_action.tool_name, 
            parameters=parsed_action.parameters
        )
        
        return response
