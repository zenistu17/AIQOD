import React, { useState } from "react";
import "./App.css";

function App() {
  const [selectedModel, setSelectedModel] = useState("openai");
  const [transcript, setTranscript] = useState("");
  const [summary, setSummary] = useState("");
  const [actionItems, setActionItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [customPrompt, setCustomPrompt] = useState(
    "Summarize the following meeting transcript in a concise and professional manner. Focus on the key discussion points, decisions, and conclusions. Format the summary in a clean, readable way with bullet points and paragraphs."
  );

  const handleFileSelection = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleGenerateSummary = async () => {
    if (!selectedFile) {
      alert("Please select an audio or video file first.");
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("audio", selectedFile);
    formData.append("model", selectedModel);
    formData.append("customPrompt", customPrompt);

    try {
      const response = await fetch("https://5343-2401-4900-634f-fe94-39ed-a7c1-2f5-86c9.ngrok-free.app/process_audio", {
        method: "POST",
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const data = await response.json();
      setTranscript(data.transcript);
      setSummary(data.summary_data.summary);
      setActionItems(data.summary_data.action_items);
    } catch (error) {
      console.error("Error processing audio:", error);
      alert("Failed to process audio. Check the console for details.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="glass-morphism-card">
        <h1 className="app-title">Meeting Summarizer</h1>
        
        <div className="input-section">
          <div className="model-select-wrapper">
            <label className="model-select-label">Select AI Model:</label>
            <select
              className="model-select"
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              name="model"
            >
              <option value="openai">Gpt-4</option>
              <option value="local">Llama-3.3</option>
            </select>
          </div>
          
          <div className="file-upload-wrapper">
            <input
              type="file"
              accept="audio/*,video/*"
              onChange={handleFileSelection}
              className="file-input"
              id="audio-upload"
              name="audio"
            />
            <label htmlFor="audio-upload" className="file-upload-button">
              {selectedFile ? selectedFile.name : "📂 Select Meeting Audio/Video"}
            </label>
          </div>
        </div>
        
        <div className="prompt-section">
          <label htmlFor="custom-prompt" className="prompt-label">Custom Summary Prompt:</label>
          <textarea
            id="custom-prompt"
            className="prompt-textarea"
            value={customPrompt}
            onChange={(e) => setCustomPrompt(e.target.value)}
            rows={4}
            placeholder="Enter custom prompt for summary generation..."
          />
          
          <button 
            className="generate-button"
            onClick={handleGenerateSummary}
            disabled={loading || !selectedFile}
          >
            {loading ? "Processing..." : "Generate Summary"}
          </button>
        </div>
        
        {loading && <div className="loader"></div>}
        
        <div className="results-section-horizontal">
          <div className="result-card-horizontal transcript-card">
            <h2>Transcript</h2>
            <p>{transcript || "Transcript will appear here..."}</p>
          </div>
          
          <div className="result-card-horizontal summary-card">
            <h2>Meeting Summary</h2>
            <p>{summary || "Summary will be generated..."}</p>
          </div>
          
          <div className="result-card-horizontal action-items-card">
            <h2>Action Items</h2>
            {actionItems && actionItems.length > 0 ? (
              <ul>
                {actionItems.map((item, index) => (
                  <li key={index} className="action-item">
                    <span className="task">{item.task}</span>
                    <span className="assignee">👤 {item.assignee}</span>
                    <span className="deadline">📅 {item.deadline}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p>No action items generated yet.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;