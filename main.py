from flask import Flask, request, jsonify
from hugchat import hugchat
from hugchat.login import Login
from flask_cors import cross_origin
from flask_cors import CORS
import os
import json
import datetime

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
                                    f"Do not create more than 5 subtasks. Keep titles and descriptions to the point. Keep the description to 1 short sentence. \n" 
                                    f"Do not use extra whitespace. {user_message}")
        message_str = message_result.wait_until_done()

        return jsonify({"response": json.loads(message_str) }) 
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/task-recognition', methods=['POST'])
@cross_origin()
def task_recognition():
    try:
        data = request.json
        user_message = data.get("message", "")

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Generate response from HuggingChat for task recognition
        recognition_result = chatbot.chat(f"You are an AI which will detect readable tasks from a user's input into a JSON format. \n"
                                          f"Respond with a minified JSON format only, following this schema:\n"
                                          f"For example: .\n"
                                          f"User input: 'Call Mom at 5' .\n"
                                          f"The current date and time is: " + datetime.datetime.now(datetime.timezone.utc).isoformat() + ". Use this for reference if the user mentions a date.\n"
                                            f"AI response: '[{{\"name\": \"Call Mom\", \"important\": true, \"description\": \"at 5\"}}]'\n"
                                          f"Only add description or date if user communicates this. End date is optional, and only add this if the user specifies this. Dates will always be in UTC timezone.\n"
                                          f"To save tokens, n = name, i = important, s = start date, e = end date, d = description: \n"
                                          f"Only write data following the schema below: \n"
                                          f"[{{\"n\": \"...\", \"i\": true/false,  \"s\": \"(ISO format date)\", \"e\": \"(ISO format date)\",  \"d\": \"...\"}}]\n"
                                          f"Do not add any extra text or whitespace. \n The following user input is below the dashed line \n -------- \n {user_message}")
        recognition_str = recognition_result.wait_until_done()

        return jsonify(json.loads(recognition_str)) 
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/filters', methods=['POST'])
@cross_origin()
def filters():
    try:
        data = request.json
        user_message = data.get("message", "")

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Generate response from HuggingChat for filters
        filters_result = chatbot.chat(f"You are an AI which will filter tasks based on user input. \n"
                                    f"Respond with a minified JSON format only, following this schema: \n"
                                    f"User input: 'Show me all tasks that are important' \n"
                                    f"AI response: '[{{\"important\": true }}]' \n"
                                    f"Only write data following the schema below: \n"
                                    f"'[{{ important: boolean, name?: {{ contains?: string, equals?:string }}, date?: {{ gte?: string, lte?: string }} }}]' \n"
                                    f"Do not add any extra text or whitespace. Only output valid JSON. \n"
                                    f"The following user input is below the dashed line \n -------- \n {user_message}")
        filters_str = filters_result.wait_until_done()

        return jsonify(json.loads(filters_str)) 
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8000)