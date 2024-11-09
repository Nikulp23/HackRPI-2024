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

  // YOLO PART
  const objectDetection = async() => {

    try {
      const response = await fetch('http://127.0.0.1:5000/recognizeObjects', {
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
  }

  return (
    <div className="App">
      <header className="App-header">

        <button onClick={objectDetection}>CLICK WHEN IMAGE IS UPLOADED</button>

        <div>
          <h2>API Responses</h2>
          <p><strong>GET IMAGE COORDINATES:</strong> {objectDetection}</p>
        </div>
      </header>
    </div>
  );
}

export default App;