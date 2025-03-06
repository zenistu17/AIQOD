import os
import librosa
import requests
import openai
import torch
import re
from transformers import (
    WhisperProcessor,
    WhisperForConditionalGeneration,
)
from huggingface_hub import InferenceClient

# Set device to CPU (MPS has limitations)
device = "cpu"
print(f"Using device: {device}")

# Load Whisper model for transcription
processor = WhisperProcessor.from_pretrained("openai/whisper-small")
whisper_model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small").to(device)
whisper_model.config.use_cache = False  # Disable KV cache
whisper_model.gradient_checkpointing_enable()  # Enable gradient checkpointing

# Initialize Hugging Face Inference Client
client = InferenceClient(
    provider="sambanova",  # Replace with the correct provider if different
    api_key=os.getenv("HUGGINGFACE_API_KEY")  # Set your Hugging Face API key in environment variables
)

def transcribe_audio(audio_file_path, chunk_size=20, overlap=5):
    """
    Transcribe audio to text using Whisper in chunks.
    If the audio is not in English, it will be translated to English.
    """
    try:
        # Load audio
        audio, sr = librosa.load(audio_file_path, sr=16000)
        print(f"Audio length: {len(audio)/sr:.2f} seconds")

        # Calculate step size and chunk size in samples
        step_samples = int((chunk_size - overlap) * sr)
        chunk_samples = int(chunk_size * sr)

        transcripts = []

        # Process audio in chunks
        for i in range(0, len(audio), step_samples):
            chunk = audio[i:i + chunk_samples]
            if len(chunk) < 0.5 * chunk_samples:  # Skip very small chunks
                break

            # Process the chunk
            input_features = processor(chunk, sampling_rate=sr, return_tensors="pt").input_features
            input_features = input_features.to(device)

            # Create attention mask
            attention_mask = torch.ones_like(input_features)

            # Generate transcription for the chunk
            with torch.no_grad():
                predicted_ids = whisper_model.generate(
                    input_features,
                    attention_mask=attention_mask,
                    max_length=448,
                    task="translate",  # Translate to English
                )

            # Decode transcription for the chunk
            transcript = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
            transcripts.append(transcript)

        # Combine all transcripts into a single string
        full_transcript = " ".join(transcripts)
        print(f"Full transcript length: {len(full_transcript)} characters, {len(full_transcript.split())} words")
        return full_transcript

    except Exception as e:
        print(f"Error in transcribe_audio: {str(e)}")
        return ""

def extract_detailed_action_items(text):
    """
    Extract action items using Llama-3.3-70B-Instruct hosted on Hugging Face via OpenAI API.
    """
    try:
        # Create a prompt for action item extraction
        prompt = f"""
        Extract specific action items from the following meeting transcript. For each action item, include:
        - Task: A clear description of the task.
        - Assignee: The person responsible for the task.
        - Deadline: The suggested timeline for completion.

        Format the action items as follows:
        - Task: [Task description]
        - Assignee: [Assignee name]
        - Deadline: [Deadline]

        Transcript:
        {text}
        """

        # Prepare messages for the chat completion API
        messages = [
            {"role": "user", "content": prompt}
        ]

        # Call the hosted Llama-3.3-70B-Instruct model via OpenAI API
        completion = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct",  # Updated model name
            messages=messages,
            max_tokens=300,  # Adjust based on desired output length
            temperature=0.7,  # Control creativity
        )

        # Extract the action items from the response
        action_items_text = completion.choices[0].message.content

        # Parse the action items into a list of dictionaries
        action_items = []
        for block in action_items_text.split("\n\n"):  # Split by paragraphs
            task = None
            assignee = "Unassigned"
            deadline = "Not specified"

            for line in block.split("\n"):
                if line.strip().startswith("- Task:"):
                    task = line.replace("- Task:", "").strip()
                elif line.strip().startswith("- Assignee:"):
                    assignee = line.replace("- Assignee:", "").strip()
                elif line.strip().startswith("- Deadline:"):
                    deadline = line.replace("- Deadline:", "").strip()

            if task:  # Only add if a task was found
                action_items.append({
                    "task": task,
                    "assignee": assignee,
                    "deadline": deadline
                })

        # If no action items are found, add a default one
        if not action_items:
            action_items.append({
                "task": "Review the meeting transcript and identify specific action items.",
                "assignee": "Unassigned",
                "deadline": "Not specified"
            })

        print(f"Extracted action items: {action_items}")
        return action_items

    except Exception as e:
        print(f"Error in extract_detailed_action_items: {str(e)}")
        return [{
            "task": "Error extracting action items.",
            "assignee": "Unassigned",
            "deadline": "Not specified"
        }]

def summarize_with_llama(text):
    """
    Summarize text using Llama-3.3-70B-Instruct hosted on Hugging Face via OpenAI API.
    """
    try:
        # Create a detailed prompt for summarization
        prompt = f"""
        Summarize the following meeting transcript in a concise and professional manner. 
        Focus on the key discussion points, decisions, and conclusions. Do not include action items.

        Format the summary in a clean, readable way with bullet points and paragraphs.

        Transcript:
        {text}
        """

        # Prepare messages for the chat completion API
        messages = [
            {"role": "user", "content": prompt}
        ]

        # Call the hosted Llama-3.3-70B-Instruct model via OpenAI API
        completion = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct",  # Updated model name
            messages=messages,
            max_tokens=500,  # Adjust based on desired summary length
            temperature=0.7,  # Control creativity
        )

        # Extract the summary from the response
        summary = completion.choices[0].message.content
        print(f"Generated summary length: {len(summary)} characters")
        return summary

    except Exception as e:
        print(f"Error in summarize_with_llama: {str(e)}")
        return ""

def generate_local_summary(text):
    """
    Generate a summary using Llama-3.3-70B-Instruct.
    """
    summary = summarize_with_llama(text)
    action_items = extract_detailed_action_items(text)
    return {
        "summary": summary or "No significant summary could be generated.",
        "action_items": action_items or [{"task": "No specific action items identified.", "assignee": "Unassigned", "deadline": "Not specified"}]
    }

def summarize_and_extract_action_items(text, use_openai=False):
    try:
        if use_openai:
            # Ensure OpenAI API key is set
            if not os.getenv("OPENAI_API_KEY"):
                print("OpenAI API key is not set. Falling back to local model.")
                return generate_local_summary(text)
            
            print("Using OpenAI for summarization and action item extraction.")  # Log OpenAI usage
            try:
                openai.api_key = os.getenv("OPENAI_API_KEY")
                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",  # Ensure the correct model name is used
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are an expert meeting summarizer. Provide a comprehensive summary and identify clear action items."
                        },
                        {
                            "role": "user", 
                            "content": f"""
                            Analyze the following meeting transcript:

                            {text}

                            Please provide:
                            1. A concise, professional summary of the transcript and list out the key discussion points.
                            2. Specific, actionable items with potential assignees and deadlines. Note that you are supposed to give at least one action item minimum.

                            Format:
                            **Summary:**
                            [Concise overview of the meeting along with key takeaways]

                            **Action Items:**
                            - Task: [Specific action]
                            - Assignee: [Who should do it]
                            - Deadline: [Suggested timeline]
                            """
                        }
                    ],
                    temperature=0.3,
                    max_tokens=500
                )
                output = response.choices[0].message.content
                return parse_openai_output(output)
            except Exception as e:
                print(f"OpenAI API call failed: {str(e)}")
                return generate_local_summary(text)
        
        # Local method if OpenAI is not used
        print("Using local model for summarization and action item extraction.")  # Log local model usage
        return generate_local_summary(text)
    
    except Exception as e:
        return {
            "summary": f"Error generating summary: {str(e)}",
            "action_items": [{"task": "Summary generation failed", "assignee": "N/A", "deadline": "N/A"}]
        }

def parse_openai_output(output):
    # Parse OpenAI generated summary and action items
    try:
        summary_match = re.search(r"\*\*Summary:\*\*\s*(.*?)\s*\*\*Action Items:\*\*", output, re.DOTALL)
        action_items_match = re.findall(r"- Task: (.*?)\n- Assignee: (.*?)\n- Deadline: (.*?)(?=\n- Task:|$)", output, re.DOTALL)
        
        summary = summary_match.group(1).strip() if summary_match else "No summary generated."
        
        parsed_action_items = [
            {
                "task": task.strip(),
                "assignee": assignee.strip(),
                "deadline": deadline.strip()
            } for task, assignee, deadline in action_items_match
        ]
        
        return {
            "summary": summary,
            "action_items": parsed_action_items or [{"task": "No specific action items identified.", "assignee": "Unassigned", "deadline": "Not specified"}]
        }
    except Exception:
        return {
            "summary": "Failed to parse OpenAI output",
            "action_items": [{"task": "Parsing error", "assignee": "N/A", "deadline": "N/A"}]
        }

def create_trello_task(task_name, assignee, deadline):
    try:
        url = "https://api.trello.com/1/cards"
        query = {
            "key": os.getenv("TRELLO_API_KEY"),
            "token": os.getenv("TRELLO_TOKEN"),
            "idList": os.getenv("TRELLO_ID_LIST"),
            "name": task_name,
            "desc": f"Assignee: {assignee}\nDeadline: {deadline}"
        }
        response = requests.post(url, params=query)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}