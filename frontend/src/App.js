import React, { useEffect, useState } from 'react';
import './App.css';

function App() {
  // State variables to store the response messages
  const [getMessage, setGetMessage] = useState('');
  const [postMessage, setPostMessage] = useState('');

  // Function to test GET request
  const testGetApi = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/get-data');
      const data = await response.json();
      console.log("GET response:", data);
      setGetMessage(data.message); // Save message to state
    } catch (error) {
      console.error("Error with GET request:", error);
    }
  };

  // Function to test POST request
  const testPostApi = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/post-data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ sampleData: "Hello from React!" }),
      });
      const data = await response.json();
      console.log("POST response:", data);
      setPostMessage(data.message); // Save message to state
    } catch (error) {
      console.error("Error with POST request:", error);
    }
  };

  useEffect(() => {
    testGetApi();
    testPostApi();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <div>
          <h2>API Responses</h2>
          <p><strong>GET Response:</strong> {getMessage}</p>
          <p><strong>POST Response:</strong> {postMessage}</p>
        </div>
      </header>
    </div>
  );
}

export default App;