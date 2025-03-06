import os
import librosa
import requests
import openai
import torch
import re
from transformers import (
    WhisperProcessor,
    WhisperForConditionalGeneration,
    AutoModelForCausalLM,
    AutoTokenizer,
)

# Load Whisper model for transcription
processor = WhisperProcessor.from_pretrained("openai/whisper-small")
whisper_model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small")

# Load Mistral 7B model for summarization
mistral_model_name = "mistralai/Mistral-7B-v0.1"
mistral_tokenizer = AutoTokenizer.from_pretrained(mistral_model_name, use_auth_token=True)
mistral_model = AutoModelForCausalLM.from_pretrained(mistral_model_name, use_auth_token=True)

def transcribe_audio(audio_file_path, chunk_size=30, overlap=5):
    """
    Transcribe audio to text using Whisper. If the audio is not in English,
    it will be translated to English.
    """
    audio, sr = librosa.load(audio_file_path, sr=16000)
    step_samples = (chunk_size - overlap) * sr
    chunk_samples = chunk_size * sr
    transcripts = []
    for i in range(0, len(audio), step_samples):
        chunk = audio[i:i + chunk_samples]
        if len(chunk) < chunk_samples:
            break
        input_features = processor(chunk, sampling_rate=sr, return_tensors="pt").input_features
        with torch.no_grad():
            # Use task="translate" to ensure the output is in English
            predicted_ids = whisper_model.generate(input_features, max_length=448, task="translate")
        transcript = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
        transcripts.append(transcript)
    return " ".join(transcripts)

def summarize_with_mistral(text):
    """
    Summarize text using Mistral 7B.
    """
    input_text = f"Summarize the following meeting transcript professionally. Identify the key points discussed and give them in list format.: {text}"
    input_ids = mistral_tokenizer(input_text, return_tensors="pt").input_ids

    # Generate summary
    with torch.no_grad():
        outputs = mistral_model.generate(input_ids, max_length=500, num_beams=5, early_stopping=True)

    summary = mistral_tokenizer.decode(outputs[0], skip_special_tokens=True)
    return summary

def generate_local_summary(text):
    """
    Generate a summary using Mistral 7B.
    """
    summary = summarize_with_mistral(text)
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
                    model="gpt-4",  # Ensure the correct model name is used
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

def extract_detailed_action_items(text):
    # Sophisticated action item extraction
    action_patterns = [
        r"(.*?)\s*should\s*(.*)",
        r"(.*?)\s*must\s*(.*)",
        r"Action\s*item:\s*(.*)",
        r"To\s*do:\s*(.*)",
        r"need\s*to\s*(.*)"
    ]
    
    action_items = []
    for pattern in action_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            task = match[0] if isinstance(match, tuple) else match
            cleaned_task = re.sub(r'\s+', ' ', task).strip()
            
            # More sophisticated filtering
            if (len(cleaned_task) > 20 and  # Ensure task is meaningful
                not any(keyword in cleaned_task.lower() for keyword in ['discuss', 'talk', 'meeting'])):
                action_items.append({
                    "task": cleaned_task,
                    "assignee": "Unassigned",
                    "deadline": "Not specified"
                })
    
    return action_items

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