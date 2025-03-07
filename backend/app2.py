from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import openai
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import numpy as np
import io
import os

# Initialize Flask and SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

# Load Whisper model
processor = WhisperProcessor.from_pretrained("openai/whisper-small")
whisper_model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small").to("cpu")
whisper_model.config.forced_decoder_ids = None

# OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Buffer to store audio chunks
audio_buffer = []

@app.route("/")
def home():
    return render_template("index.html")

@socketio.on("audio_chunk")
def handle_audio_chunk(chunk):
    try:
        print("Received audio chunk")  # Debug log
        audio_data = np.frombuffer(chunk, dtype=np.float32)
        print(f"Audio data shape: {audio_data.shape}")  # Debug log
        audio_buffer.append(audio_data)

        # Process the buffer every 5 seconds
        if len(audio_buffer) >= 5:  # Adjust based on chunk size
            print("Processing audio buffer")  # Debug log
            full_audio = np.concatenate(audio_buffer)
            audio_buffer.clear()

            # Transcribe the audio
            input_features = processor(full_audio, sampling_rate=16000, return_tensors="pt").input_features
            predicted_ids = whisper_model.generate(input_features)
            transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
            print(f"Transcription: {transcription}")  # Debug log

            # Emit the transcription to the frontend
            emit("transcription", transcription)

            # Generate a partial summary using GPT-4
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes meeting discussions."},
                    {"role": "user", "content": f"Summarize the following discussion:\n\n{transcription}"}
                ],
                max_tokens=100,
            )
            summary = response.choices[0].message.content
            print(f"Summary: {summary}")  # Debug log
            emit("summary", summary)
    except Exception as e:
        print(f"Error processing audio chunk: {str(e)}")

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)