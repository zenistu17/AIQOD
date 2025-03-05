import React, { useState } from "react";
import "./App.css";

function App() {
  const [selectedModel, setSelectedModel] = useState("openai");
  const [transcript, setTranscript] = useState("");
  const [summary, setSummary] = useState("");
  const [actionItems, setActionItems] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append("audio", file);
    formData.append("model", selectedModel);
    try {
      const response = await fetch("https://b906-115-99-24-216.ngrok-free.app/process_audio", {
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
    }
    setLoading(false);
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
            >
              <option value="openai">OpenAI</option>
              <option value="local">Local Inference Model</option>
            </select>
          </div>
          <div className="file-upload-wrapper">
            <input
              type="file"
              accept="audio/*"
              onChange={handleFileUpload}
              className="file-input"
              id="audio-upload"
            />
            <label htmlFor="audio-upload" className="file-upload-button">
              {loading ? 'Processing...' : '📂 Upload Meeting Audio'}
            </label>
          </div>
        </div>
        {loading && <div className="loader"></div>}
        <div className="results-section-horizontal">
          <div className="result-card-horizontal transcript-card">
            <h2>Transcript</h2>
            <p>{transcript || 'Transcript will appear here...'}</p>
          </div>
          <div className="result-card-horizontal summary-card">
            <h2>Meeting Summary</h2>
            <p>{summary || 'Summary will be generated...'}</p>
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
