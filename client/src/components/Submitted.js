import React from 'react';

function Submitted({ images }) {
  return (
    <div className="container">
      <h2>Submitted Images</h2>
      {images.length === 0 ? (
        <p>No images have been uploaded yet.</p>
      ) : (
        images.map((img, index) => (
          <img key={index} src={img.url} alt={`Submitted ${index}`} width="200" />
        ))
      )}
    </div>
  );
}

export default Submitted;

// import React, { useState, useEffect } from 'react';

// function Submitted() {
//   const [images, setImages] = useState([]);

//   useEffect(() => {
//     const fetchImages = async () => {
//       try {
//         const response = await fetch('http://localhost:5000/submitted', {
//           method: 'GET',
//           headers: {
//             'Content-Type': 'application/json',
//           },
//         });

//         if (!response.ok) {
//           throw new Error(`Error: ${response.statusText}`);
//         }

//         const data = await response.json();
//         setImages(data);
//       } catch (error) {
//         console.error('Error fetching images:', error);
//       }
//     }

//     fetchImages();
//   }, []);

//   return (
//     <div>
//       <h2>Submitted Images</h2>
//       {images.map((img, index) => (
//         <img key={index} src={img.url} alt="Submitted" width="200" />
//       ))}
//     </div>
//   );
// }

// export default Submitted;