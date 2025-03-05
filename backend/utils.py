import os
import librosa
import requests
import openai
import torch
import re
from transformers import WhisperProcessor, WhisperForConditionalGeneration, T5ForConditionalGeneration, T5Tokenizer

processor = WhisperProcessor.from_pretrained("openai/whisper-small")
whisper_model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small")

def transcribe_audio(audio_file_path, chunk_size=30, overlap=5):
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
            predicted_ids = whisper_model.generate(input_features, max_length=448)
        transcript = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
        transcripts.append(transcript)
    return " ".join(transcripts)

def summarize_and_extract_action_items(text, use_openai=False):
    try:
        if use_openai:
            # Ensure OpenAI API key is set
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                print("OpenAI API key is not set. Falling back to local model.")
                return generate_local_summary(text)
            
            try:
                openai.api_key = openai_api_key
                response = openai.ChatCompletion.create(
                    model="gpt-4",  # Use a valid model name
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
                            1. A concise, professional summary of the key discussion points, along with key discussion points in ordered format
                            2. Specific, actionable items with potential assignees
                            
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
        return generate_local_summary(text)
    
    except Exception as e:
        return {
            "summary": f"Error generating summary: {str(e)}",
            "action_items": [{"task": "Summary generation failed", "assignee": "N/A", "deadline": "N/A"}]
        }

def generate_local_summary(text):
    # Improved local summarization using T5-large model
    model_name = "t5-large"
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)
    
    # Detailed prompt for summarization
    input_text = (
        "Summarize this meeting transcript professionally. "
        "Capture the main topic, key arguments, and essential insights. "
        "Provide a clear, concise overview that highlights the core discussion: "
        f"{text}"
    )
    
    # Tokenize with increased context
    input_ids = tokenizer.encode(input_text, return_tensors="pt", max_length=1024, truncation=True)
    
    # Generate summary with enhanced parameters
    summary_ids = model.generate(
        input_ids, 
        max_length=500,
        min_length=100,
        length_penalty=2.0,
        num_beams=8,
        early_stopping=True,
        no_repeat_ngram_size=2
    )
    
    # Decode summary
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    
    # Extract action items from the full text
    action_items = extract_detailed_action_items(text)
    
    return {
        "summary": summary or "No significant summary could be generated.",
        "action_items": action_items or [{"task": "No specific action items identified.", "assignee": "Unassigned", "deadline": "Not specified"}]
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