import React, { useEffect, useState, useRef } from 'react';
import './App.css';

import FileUploadToggle from './components/buttons/FileUploadToggle'
import IdentifiedItem from './components/content/IdentifiedItem'

function App() {
  // State variables to store the response messages
  const [getMessage, setGetMessage] = useState('');
  const [postMessage, setPostMessage] = useState('');
  const [data, setData] = useState([]);

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
    const data = [{facts : "Plastic bottles are made from polyethylene terephthalate (PET) or high-density polyethylene (HDPE), both of which are highly recyclable. Recycling plastic can help reduce pollution and conserve natural resources, as producing new plastic products from recycled materials uses less energy and water compared to making them from raw materials.",
                   infoOnUse : "Plastic bottles can be recycled at most recycling centers. To properly recycle, rinse and dry the bottle to remove any liquid or residue. Check for a recycling symbol and number on the bottle to ensure it is accepted by your local recycling program.",
                   name : "Plastic Bottle",
                   use : "Recycle"},
                  
                  {facts : "Trash bags are made from polyethylene terephthalate (PET) or high-density polyethylene (HDPE), both of which are highly recyclable. Recycling plastic can help reduce pollution and conserve natural resources, as producing new plastic products from recycled materials uses less energy and water compared to making them from raw materials.",
                  infoOnUse : "Trash bags can be recycled at most recycling centers. To properly recycle, rinse and dry the bottle to remove any liquid or residue. Check for a recycling symbol and number on the bottle to ensure it is accepted by your local recycling program.",
                  name : "Trash Bag",
                  use : "Garbage"}];

    setData(data);
  }, []);


  const fileInputRef = useRef(null);
  const [imageUrl, setImageUrl] = useState(null); // State to store the uploaded image URL

  const handleUploadBoxClick = () => {
    fileInputRef.current.click();
  };

  const handleDiscardImage = () => {
    setImageUrl(null);
  }

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      console.log('Selected file:', file.name);
      uploadFile(file);
    }
  };

  const getCroppedData = async (blob, coordinates) => {
    const formData = new FormData();
    formData.append('image', blob); // Use the image from the first API response
    formData.append('coordinates', JSON.stringify(coordinates));
    console.log(formData)
  
    try {
      const response = await fetch('http://localhost:5000/api/get-sub-images', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        // const data = await response.json();
        // setData(data);
        console.log('Cropped images data:', data);
      } else {
        console.error('Failed to fetch cropped images:', response.statusText);
      }
    } catch (error) {
      console.error('Error fetching cropped images:', error);
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
        const data = await response.json();
  
        // Convert Base64 image back to Blob for display
        const base64Image = data.image;
        const binary = atob(base64Image);
        const array = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) {
          array[i] = binary.charCodeAt(i);
        }
  
        const blob = new Blob([array], { type: 'image/png' });
        const imageUrl = URL.createObjectURL(blob);
        setImageUrl(imageUrl); // Set image to display
        await getCroppedData(blob, data.croppedCoordinates);
      } else {
        console.error('Failed to fetch image:', response.statusText);
      }
    } catch (error) {
      console.error('Error uploading image:', error);
    }
  };
  
  

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
            <FileUploadToggle />
        </div>

        <div className="card">
          <div className="cardContent">

            <h2 className="cardHeader">Upload an Image</h2>
            <p className="cardText">Let's see what eco-treasures you've found!</p>
            <div className="uploadBoxContainer">
              <div className="uploadBox" onClick={handleUploadBoxClick}>
                {!imageUrl && <h4 className="clickToUpload">Click to upload</h4> }
                <input
                  type="file"
                  ref={fileInputRef}
                  style={{ display: 'none' }}
                  onChange={handleFileChange}
                />
                {imageUrl &&
                  <>
                    <div className="imageDisplayContainer">
                      <img src={imageUrl} className="imageDisplay" alt="Uploaded" style={{ maxWidth: '95%', maxHeight: '75%' }} />
                      <div className="reuploadContainer">
                        <h4 className="clickToUpload">Click to re-upload</h4>
                      </div>
                    </div>
                  </>
                }
              </div>
              {imageUrl &&
              <>
              <div className="reuploadContainer">
                <h4 className="clickToUpload">OR</h4>
              </div>
              <button className="discardImage" onClick={handleDiscardImage}>
                <h4 className="clickToUpload">Discard image</h4>
              </button>
              </>
              }
            </div>
          </div>
        </div>

        <div className="card" style={{maxHeight: "60vh", overflowY: "auto", overflowX: "hidden"}}>
          <div className="cardContent">
            <h2 className="cardHeader">Eco-Discoveries</h2>
            <p className="cardSubHeader">Let's see what we can save from the landfill!</p>

            {data[0] && <IdentifiedItem facts={data[0].facts}
                            infoOnUse={data[0].infoOnUse}
                            name={data[0].name}
                            use={data[0].use}
                            />}

            {data[1] && <IdentifiedItem facts={data[1].facts}
                            infoOnUse={data[1].infoOnUse}
                            name={data[1].name}
                            use={data[1].use}
                            />}

          </div>
        </div>

        <h2>Hi</h2>


      </div>

    </div>
  );
}

export default App;