# Local AI Assistant

This is a local, privacy-first AI Assistant powered by a Local Language Model (LLM). 

## How It Works

The assistant follows a **Tool-Based Architecture**:
1. **Input**: You send a message (like `"what is todays date"`) via the Flutter App to the local Python Flask Server running on port `5001`.
2. **Parsing**: The `AssistantEngine` passes your text to the `ActionParser`. 
3. **LLM Decision (Ollama)**: The `ActionParser` formats a prompt containing all the registered tools (Calculator, System Time, Folder Creation, etc.) and sends it to the Local LLM via HTTP on `localhost:11434`.
4. **Execution**: The LLM responds with a JSON object specifying the correct `tool` and `parameters` to use. The `ToolRegistry` executes the specified tool locally on your computer and returns the text result.

## Troubleshooting: Why does everything return "I am a local assistant..."?

If the assistant responds to `help` correctly but gives the fallback message for everything else (like `calculate 25* 10` or `list_memories`), **your Local LLM (Ollama) is not running**.

### The Flow of the Error:
1. The assistant tries to contact Ollama at `http://localhost:11434/api/generate`.
2. The connection fails because Ollama isn't started or isn't installed.
3. To prevent crashing, the system swallows the error and returns a fallback JSON: `{"intent": "UNKNOWN"}`.
4. The `ActionParser` looks for a `"tool"` key. Since it's missing, it assumes the tool is `"unknown"`.
5. The `ToolRegistry` sees the `"unknown"` tool and returns the default fallback string: `"I am a local assistant. How can I help you?..."`.

*(Note: The `"help"` command works instantly because we recently added a quick-bypass that maps it directly to the help tool without asking the LLM!)*

## Setup Instructions

To fix this and make all the commands work:
1. **Install Ollama**: If you haven't already, download and install Ollama from [ollama.com](https://ollama.com/).
2. **Start Ollama**: Open your terminal and start the Ollama application.
3. **Download the Model**: The system defaults to using `llama3`. You must pull it by running:
   ```bash
   ollama run llama3
   ```
4. **Run the Server**: Ensure this python backend is running via `python3 server.py`.

Once Ollama is running in the background, inputs like `"calculate 25 * 10"` will successfully be sent to the LLM, the LLM will recognize it as a math expression, and it will return the JSON to trigger the `calculator` tool!
