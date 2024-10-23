import React, { useState } from 'react';
import axios from 'axios';

function Improve() {
  const [description, setDescription] = useState('');
  const [imageUrl, setImageUrl] = useState('');
  const [response, setResponse] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      const { data } = await axios.post('http://localhost:8000/improve', {
        description,
        image_url: imageUrl,
      });
      setResponse(data.suggestion);
    } catch (error) {
      console.error(error);
      setResponse('An error occurred while generating suggestions.');
    }
  };

  return (
    <div className="container">
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Enter description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <input
          type="text"
          placeholder="Enter image URL"
          value={imageUrl}
          onChange={(e) => setImageUrl(e.target.value)}
        />
        <button type="submit">Submit</button>
      </form>
      {response && <p>AI Suggestion: {response}</p>}
    </div>
  );
}

export default Improve;


// import React, { useState } from 'react';
// import axios from 'axios';

// function Improve() {
//   const [prompt, setPrompt] = useState('');
//   const [response, setResponse] = useState('');

//   const handleSubmit = async (event) => {
//     event.preventDefault();
//     const { data } = await axios.post('http://localhost:5000/improve', { prompt });
//     setResponse(data.suggestion);
//   };

//   return (
//     <div className="container">
//       <form onSubmit={handleSubmit}>
//         <input
//           type="text"
//           placeholder="Enter your prompt"
//           value={prompt}
//           onChange={(e) => setPrompt(e.target.value)}
//         />
//         <button type="submit">Submit</button>
//       </form>
//       {response && <p>AI Suggestion: {response}</p>}
//     </div>
//   );
// }

// export default Improve;