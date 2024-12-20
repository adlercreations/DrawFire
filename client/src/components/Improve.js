import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import axios from 'axios';

function Improve() {
  const location = useLocation();
  const imageUrl = new URLSearchParams(location.search).get('imageUrl');

  const [images, setImages] = useState([]); // Store all uploaded images
  const [selectedImageUrl, setSelectedImageUrl] = useState(imageUrl || null);
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [prompt, setPrompt] = useState('');
  const [showPromptInput, setShowPromptInput] = useState(false);

  useEffect(() => {
    if (!selectedImageUrl) {
      // Fetch all images if no specific image URL is provided
      const fetchImages = async () => {
        try {
          const { data } = await axios.get('http://localhost:8000/submitted');
          setImages(data);
        } catch (error) {
          console.error('Error fetching images:', error);
        }
      };
      fetchImages();
    }
  }, [selectedImageUrl]);

  const handleGenerateSuggestion = async () => {
    setResponse('');
    setLoading(true);

    try {
      const { data } = await axios.post('http://localhost:8000/improve', {
        image_url: selectedImageUrl,
        initial_prompt: prompt,
      });
      setResponse(data.suggestion);
    } catch (error) {
      console.error('Error generating suggestions:', error);
      setResponse('Failed to generate suggestions.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="main-container">
      <h2>Improve Your Image</h2>
      {selectedImageUrl ? (
        <div>
          <img
            src={selectedImageUrl}
            alt="Selected for improvement"
            width="300"
            onClick={() => setShowPromptInput(true)}
            style={{ cursor: 'pointer', margin: '10px' }}
          />
          {showPromptInput && (
            <div>
              <textarea
                placeholder="Enter a description for the AI"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                className="prompt-input"
              />
              <button onClick={handleGenerateSuggestion}>Generate Suggestion</button>
            </div>
          )}
        </div>
      ) : (
        <div className="image-gallery">
          {images.map((img, index) => (
            <img
              key={index}
              src={img.url}
              alt={`Uploaded ${index}`}
              width="200"
              onClick={() => {
                setSelectedImageUrl(img.url);
                setShowPromptInput(true);
              }}
              style={{ cursor: 'pointer', margin: '10px' }}
            />
          ))}
          {showPromptInput && (
            <div>
              <textarea
                placeholder="Enter a description for the AI"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                className="prompt-input"
              />
              <button onClick={handleGenerateSuggestion}>Generate Suggestion</button>
            </div>
          )}
        </div>
      )}
      {loading && <p>Generating suggestions, please wait...</p>}
      {response && (
        <div className="suggestions-container">
          <h3>AI Suggestion:</h3>
          <p>{response}</p>
        </div>
      )}
    </div>
  );
}

export default Improve;



// import React, { useState, useEffect } from 'react';

// import axios from 'axios';

// function Improve() {
//   const [images, setImages] = useState([]); // Store submitted images
//   const [response, setResponse] = useState(''); // Store AI suggestions
//   const [loading, setLoading] = useState(false); // Loading state

//   // Fetch submitted images from the backend when the component mounts
//   useEffect(() => {
//     const fetchImages = async () => {
//       try {
//         const { data } = await axios.get('http://localhost:8000/submitted');
//         setImages(data);
//       } catch (error) {
//         console.error('Error fetching images:', error);
//       }
//     };
//     fetchImages();
//   }, []);

//   // Handle image selection and generate suggestions
//   const handleImageClick = async (image) => {
//     setResponse(''); // Clear previous responses
//     setLoading(true); // Set loading state

//     try {
//       const { data } = await axios.post('http://localhost:8000/improve', {
//         image_url: image.url,
//         description: 'This is my uploaded drawing. How can I improve it?',
//       });
//       setResponse(data.suggestion); // Store AI suggestions
//     } catch (error) {
//       console.error('Error generating suggestions:', error);
//       setResponse('Failed to generate suggestions.');
//     } finally {
//       setLoading(false); // Clear loading state
//     }
//   };

//   return (
//     <div className="main-container">
//       <h2>Select an Image to Improve</h2>
//       <div className="image-gallery">
//         {images.length === 0 ? (
//           <p>No images available. Please upload an image first.</p>
//         ) : (
//           images.map((img, index) => (
//             <img
//               key={index}
//               src={img.url}
//               alt={`Uploaded ${index}`}
//               width="200"
//               onClick={() => handleImageClick(img)} // Trigger on click
//               style={{ cursor: 'pointer', margin: '10px' }}
//             />
//           ))
//         )}
//       </div>

//       {loading && <p>Processing image, please wait...</p>}

//       {response && (
//         <div className="suggestions-container">
//           <h3>AI Suggestion:</h3>
//           <p>{response}</p>
//         </div>
//       )}
//     </div>
//   );
// }

// export default Improve;
