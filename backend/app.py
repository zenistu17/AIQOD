from flask import Flask, request, jsonify
from flask_cors import CORS
from utils import transcribe_audio, summarize_and_extract_action_items, create_trello_task
import os
import time
import logging
from moviepy.editor import VideoFileClip  # Import moviepy for video handling

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

def extract_audio_from_video(video_file_path, audio_file_path):
    """
    Extract audio from a video file and save it as a WAV file.
    """
    try:
        # Load the video file
        video_clip = VideoFileClip(video_file_path)
        
        # Extract audio and save as WAV
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(audio_file_path, fps=16000)  # Set sample rate to 16000 Hz
        
        # Close the clips to free up resources
        audio_clip.close()
        video_clip.close()
        
        logger.info(f"Extracted audio from video and saved to {audio_file_path}")
        return True
    except Exception as e:
        logger.error(f"Error extracting audio from video: {str(e)}")
        return False

@app.route("/")
def home():
    return jsonify({"message": "Flask backend is running!"})

@app.route("/process_audio", methods=["POST"])
def process_audio():
    try:
        file = request.files.get("audio")
        selected_model = request.form.get("model", "openai")  # Get model choice
        
        if not file:
            logger.error("No file provided")
            return jsonify({"error": "No file provided"}), 400

        # Create temp directory if it doesn't exist
        os.makedirs("temp", exist_ok=True)
        
        # Use timestamp to avoid filename conflicts
        timestamp = int(time.time())
        filepath = f"temp/file_{timestamp}"
        audio_file_path = f"temp/audio_{timestamp}.wav"
        
        try:
            # Save the uploaded file (could be audio or video)
            file.save(filepath)
            logger.info(f"Saved uploaded file to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save file: {str(e)}")
            return jsonify({"error": f"Failed to save file: {str(e)}"}), 500

        # Check if the file is a video and extract audio
        if file.filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
            logger.info(f"Detected video file: {file.filename}")
            if not extract_audio_from_video(filepath, audio_file_path):
                return jsonify({"error": "Failed to extract audio from video"}), 500
        else:
            logger.info(f"Detected audio file: {file.filename}")
            audio_file_path = filepath  # Use the uploaded file directly as audio

        logger.info(f"Starting transcription of {audio_file_path}")
        transcript = transcribe_audio(audio_file_path)
        
        if not transcript:
            logger.error("Failed to transcribe audio")
            return jsonify({"error": "Failed to transcribe audio"}), 500
            
        logger.info(f"Transcription complete. Length: {len(transcript)} characters")
        logger.info(f"Starting summary generation using model: {selected_model}")
        
        use_openai = selected_model == "openai"  # Convert to boolean
        summary_data = summarize_and_extract_action_items(transcript, use_openai=use_openai)
        
        action_items = summary_data.get("action_items", [])
        
        # Only create Trello tasks if we have action items and Trello API keys are set
        trello_responses = []
        if action_items and os.getenv("TRELLO_API_KEY") and os.getenv("TRELLO_TOKEN"):
            logger.info(f"Creating {len(action_items)} Trello tasks")
            for item in action_items:
                if isinstance(item, dict) and all(key in item for key in ["task", "assignee", "deadline"]):  # Validate action item format
                    trello_response = create_trello_task(item["task"], item["assignee"], item["deadline"])
                    trello_responses.append(trello_response)
                else:
                    logger.warning(f"Invalid action item format: {item}")
        
        # Clean up the temporary files
        try:
            os.remove(filepath)
            logger.info(f"Removed temporary file {filepath}")
            if filepath != audio_file_path:  # Remove the extracted audio file if it's different
                os.remove(audio_file_path)
                logger.info(f"Removed temporary audio file {audio_file_path}")
        except Exception as e:
            logger.warning(f"Could not remove temporary file: {str(e)}")
        
        return jsonify({
            "transcript": transcript, 
            "summary_data": summary_data, 
            "trello_responses": trello_responses
        })
    
    except Exception as e:
        logger.error(f"Error in process_audio: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)