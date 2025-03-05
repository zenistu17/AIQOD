from flask import Flask, request, jsonify
from flask_cors import CORS
from utils import transcribe_audio, summarize_and_extract_action_items, create_trello_task

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

@app.route("/")
def home():
    return jsonify({"message": "Flask backend is running!"})

@app.route("/process_audio", methods=["POST"])
def process_audio():
    try:
        file = request.files.get("audio")
        selected_model = request.form.get("model", "openai")  # Get model choice
        
        if not file:
            return jsonify({"error": "No audio file provided"}), 400

        filepath = "temp_audio.wav"
        try:
            file.save(filepath)
        except Exception as e:
            return jsonify({"error": f"Failed to save file: {str(e)}"}), 500

        transcript = transcribe_audio(filepath)
        
        use_openai = selected_model == "openai"  # Convert to boolean
        summary_data = summarize_and_extract_action_items(transcript, use_openai=use_openai)
        action_items = summary_data.get("action_items", [])
        
        trello_responses = [create_trello_task(item["task"], item["assignee"], item["deadline"]) for item in action_items]
        
        return jsonify({"transcript": transcript, "summary_data": summary_data, "trello_responses": trello_responses})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
