# Meeting Summarizer 🎙️📝

## Project Banner
Automate your meeting notes with AI-powered transcription, summarization, and action item extraction.

## Overview
The Meeting Summarizer is an AI-powered tool designed to streamline your meeting workflows. It transcribes audio/video recordings of meetings, generates concise summaries, and extracts actionable tasks with assignees and deadlines. Whether you're using OpenAI GPT-4 or Llama-3.3-70B-Instruct, this tool ensures you never miss a key discussion point or action item.

## Features ✨
- **Audio/Video Transcription**: Transcribe meeting recordings into text using OpenAI Whisper.
- **AI-Powered Summarization**: Generate concise and professional summaries of meeting transcripts.
- **Action Item Extraction**: Extract specific tasks, assignees, and deadlines from the transcript.
- **Customizable Prompts**: Modify the summary generation prompt to suit your needs.
- **Multi-Model Support**: Choose between OpenAI GPT-4 and Llama-3.3-70B-Instruct for summarization.
- **Trello Integration**: Automatically create Trello tasks for extracted action items.

## Tech Stack 🛠️
- **Frontend**: React.js, HTML, CSS
- **Backend**: Flask (Python)
- **AI Models**:
  - Transcription: OpenAI Whisper
  - Summarization: OpenAI GPT-4 or Llama-3.3-70B-Instruct
- **APIs**:
  - Hugging Face Inference API (for Llama)
  - OpenAI API (for GPT-4 and Whisper)
  - Trello API (for task creation)

## Installation 🚀

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API Key
- Hugging Face API Key (for Llama)
- Trello API Key and Token (optional)

### Backend Setup
1. Clone the repository:
```bash
git clone https://github.com/your-username/meeting-summarizer.git
cd meeting-summarizer/backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   Create a `.env` file in the backend directory and add the following:
```
OPENAI_API_KEY=your_openai_api_key
HUGGINGFACE_API_KEY=your_huggingface_api_key
TRELLO_API_KEY=your_trello_api_key
TRELLO_TOKEN=your_trello_token
TRELLO_ID_LIST=your_trello_list_id
```

4. Run the Flask server:
```bash
python app.py
```

### Frontend Setup
1. Navigate to the frontend directory:
```bash
cd ../frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Start the React development server:
```bash
npm start
```

4. Open your browser and go to http://localhost:3000.

## Usage 📖
1. **Upload a File**:
   - Upload an audio or video file of your meeting.
   - The tool will transcribe the file using OpenAI Whisper.

2. **Edit the Prompt (Optional)**:
   - Modify the custom prompt for summary generation if needed.

3. **Generate Summary**:
   - Click the Generate button to create a summary and extract action items.

4. **View Results**:
   - The transcript, summary, and action items will be displayed on the screen.
   - Action items can be automatically added to Trello (if configured).

## Screenshots 📸
- **Upload File**: Upload a meeting recording.
- **Summary and Action Items**: View the transcript, summary, and action items.

## Configuration ⚙️
### Custom Prompts
You can customize the summary generation prompt by editing the text in the Custom Summary Prompt textbox. For example:

```
Please provide:
1. A concise, professional summary of the transcript and list out the key discussion points.
2. Name of the people involved in the meeting.
3. What are the deadline dates?
```

### Trello Integration
To enable Trello integration:
1. Create a Trello board and list.
2. Obtain your Trello API Key, Token, and List ID.
3. Add these credentials to the `.env` file.

## Contributing 🤝
Contributions are welcome! If you'd like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeatureName`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/YourFeatureName`).
5. Open a pull request.

## License 📜
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments 🙏
- OpenAI for Whisper and GPT-4.
- Hugging Face for Llama-3.3-70B-Instruct.
- Trello for task management integration.

## Contact 📧
For questions or feedback, feel free to reach out:
- Email: sujithsures@gmail.com
- GitHub: [GitHub](https://github.com/zenistu17)
- LinkedIn: [Your Name](https://www.linkedin.com/in/sujith-s-62aa7527a/)

---

Made with ❤️ by Sujith. Happy summarizing! 🚀
