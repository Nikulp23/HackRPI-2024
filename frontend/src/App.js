import React, { useEffect, useState, useRef } from 'react';
import './App.css';

import FileUpload from './components/buttons/FileUpload'

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

  const fileInputRef = useRef(null);

  const handleUploadBoxClick = () => {
    fileInputRef.current.click();
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      console.log('Selected file:', file.name);
      uploadFile(file);
    }
  };

  const uploadFile = async (file) => {
    const formData = new FormData();
      formData.append('image', file);

      try {
        const response = await fetch('http://localhost:5000/api/upload-image', {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          const blob = await response.blob();
          const url = URL.createObjectURL(blob);
          // setImageUrl(url);
        } else {
          console.error('Failed to fetch image:', response.statusText);
        }
      } catch (error) {
        console.error('Error uploading image:', error);
      }
  }

  return (
    <div className="App">
      <header className="App-header">
        <div>
          {/* <h2>API Responses</h2>
          <p><strong>GET Response:</strong> {getMessage}</p>
          <p><strong>POST Response:</strong> {postMessage}</p> */}

          <h2>Eco-Friendly Recycling Buddy</h2>
        </div>
      </header>

      <div className="content">
        <div className="uploadButtons">
            <FileUpload />
        </div>

        <div className="card">
          <div className="cardContent">
            <h2 className="cardHeader">Upload an Image</h2>
            <p className="cardSubHeader">Let's see what eco-treasures you've found!</p>
            <div className="uploadBoxContainer">
              <div className="uploadBox" onClick={handleUploadBoxClick}>
                <h4 className="clickToUpload">Click to upload</h4>
                <input
                  type="file"
                  ref={fileInputRef}
                  style={{ display: 'none' }}
                  onChange={handleFileChange}
                />
              </div>
            </div>
          </div>
        </div>
        <div className="card">
          
        </div>
      </div>

    </div>
  );
}

export default App;