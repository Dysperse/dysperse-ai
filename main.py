from flask import Flask, request, jsonify
from hugchat import hugchat
from hugchat.login import Login
from flask_cors import cross_origin
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

cookie_path_dir = "./cookies/"  
sign = Login("manusvathgurudath@gmail.com", os.environ.get("PASSWD"))
cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=True)

# Create the ChatBot
chatbot = hugchat.ChatBot(cookies=cookies.get_dict())

@app.route('/subtasks', methods=['POST'])
@cross_origin()
def chat():
    try:
        data = request.json
        user_message = data.get("message", "")

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Generate response from HuggingChat
        message_result = chatbot.chat(f"You are an AI which will split this task into smaller, manageable subtasks which are relevant to achieve the task.\n" 
                                    f"You will provide data in a minified JSON format only, without any surrouding or extra text.\n" 
                                    f"You must follow this schema: [ {{ \"title\": \"...\", \"description\": \"...\" }} ] \n" 
                                    f"Do not create more than 5 subtasks. Keep titles and descriptions to the point. If a description is not necessary or repetitive, omit it. \n" 
                                    f"Do not use extra whitespace. {user_message}")
        message_str = message_result.wait_until_done()

        return jsonify({"response": json.loads(message_str) }) 
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8000)