import React, { useState } from "react";

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
    formData.append("model", selectedModel);  // Send selected model
    
    try {
      const response = await fetch("http://127.0.0.1:5000/process_audio", {
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
    <div>
      <h1>Meeting Summarizer</h1>
      <label>
        Select Model:
        <select onChange={(e) => setSelectedModel(e.target.value)}>
          <option value="openai">OpenAI</option>
          <option value="local">Local Model</option>
        </select>
      </label>
      <input type="file" accept="audio/*" onChange={handleFileUpload} />
      {loading && <p>Processing...</p>}
      <h2>Transcript</h2>
      <p>{transcript}</p>
      <h2>Summary</h2>
      <p>{summary}</p>
      <h2>Action Items</h2>
      <ul>
        {(actionItems || []).map((item, index) => (
          <li key={index}>{item.task} - {item.assignee} (Deadline: {item.deadline})</li>
        ))}
      </ul>
    </div>
  );
}

export default App;
