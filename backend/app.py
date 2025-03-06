/* App.css */
:root {
  --primary-color: #6c63ff;
  --secondary-color: #f5f5f5;
  --text-color: #333;
  --card-bg: rgba(255, 255, 255, 0.8);
  --gradient-start: #8e2de2;
  --gradient-end: #4a00e0;
  --shadow-color: rgba(0, 0, 0, 0.1);
}

body {
  margin: 0;
  font-family: 'Segoe UI', 'Roboto', sans-serif;
  background: linear-gradient(135deg, var(--gradient-start), var(--gradient-end));
  min-height: 100vh;
  color: var(--text-color);
  padding: 20px;
}

.app-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.glass-morphism-card {
  background: var(--card-bg);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 8px 32px 0 var(--shadow-color);
  border: 1px solid rgba(255, 255, 255, 0.18);
}

.app-title {
  text-align: center;
  margin-bottom: 30px;
  color: var(--primary-color);
  font-size: 2.5rem;
}

.input-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 30px;
}

.model-select-wrapper {
  display: flex;
  align-items: center;
  gap: 15px;
}

.model-select-label {
  font-weight: 600;
}

.model-select {
  padding: 10px 15px;
  border-radius: 8px;
  border: 1px solid #ddd;
  background-color: white;
  font-size: 1rem;
  cursor: pointer;
}

.file-type-toggle {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-bottom: 10px;
}

.toggle-button {
  padding: 10px 20px;
  border-radius: 8px;
  border: 1px solid #ddd;
  background-color: white;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.toggle-button.active {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.file-upload-wrapper {
  text-align: center;
}

.file-input {
  display: none;
}

.file-upload-button {
  display: inline-block;
  padding: 12px 24px;
  background-color: var(--primary-color);
  color: white;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.file-upload-button:hover {
  background-color: #5a52d5;
  transform: translateY(-2px);
}

.loader {
  border: 5px solid #f3f3f3;
  border-top: 5px solid var(--primary-color);
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 2s linear infinite;
  margin: 20px auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.results-section-horizontal {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.result-card-horizontal {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px var(--shadow-color);
  height: 300px;
  overflow-y: auto;
}

.result-card-horizontal h2 {
  color: var(--primary-color);
  margin-top: 0;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.transcript-card {
  border-left: 4px solid #4caf50;
}

.summary-card {
  border-left: 4px solid #2196f3;
}

.action-items-card {
  border-left: 4px solid #ff9800;
}

.action-item {
  margin-bottom: 15px;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.task {
  font-weight: 600;
}

.assignee, .deadline {
  font-size: 0.9rem;
  color: #666;
}

/* Responsive design */
@media (max-width: 768px) {
  .results-section-horizontal {
    grid-template-columns: 1fr;
  }
  
  .input-section {
    gap: 15px;
  }
  
  .model-select-wrapper {
    flex-direction: column;
    align-items: flex-start;
  }
}
