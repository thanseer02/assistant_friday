from flask import Flask, request, jsonify
# We need flask_cors to allow the Flutter UI to make requests to this server
from flask_cors import CORS
from assistant.engine import AssistantEngine

app = Flask(__name__)
CORS(app)

# Initialize the core engine once when the server starts
engine = AssistantEngine()

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Receives JSON containing {"message": "user text"}
    Returns JSON containing {"response": "assistant text"}
    """
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "No message provided"}), 400
        
    user_message = data['message']
    
    try:
        # The engine processes the text just like it did in the terminal
        response = engine.process(user_message)
        return jsonify({"response": response})
    except Exception as e:
        print(f"[Server Error] {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("=========================================================")
    print("  Starting Local Assistant Backend (http://0.0.0.0:5001)")
    print("=========================================================")
    # Bind to 0.0.0.0 so external devices on the same Wi-Fi can connect
    app.run(host='0.0.0.0', port=5001, debug=True)
