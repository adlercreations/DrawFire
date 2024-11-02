import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function Submitted({ images, setImages }) {
  const navigate = useNavigate();

  useEffect(() => {
    const fetchImages = async () => {
      const response = await fetch('http://localhost:8000/submitted');
      const data = await response.json();
      setImages(data);
    }
    fetchImages();
  }, [setImages]);

  const handleImageClick = (url) => {
    navigate(`/improve?imageUrl=${encodeURIComponent(url)}`);
  };
  
  return (
    <div className="container">
      <h2>Submitted Images</h2>
      {images.length === 0 ? (
        <p>No images have been uploaded yet.</p>
      ) : (
        <div className="image-gallery">
          {images.map((img, index) => (
            <img 
              key={index}
              src={img.url}
              alt={`Submitted ${index}`}
              width="200"
              onClick={() => handleImageClick(img.url)}
              style={{ cursor: 'pointer' }}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default Submitted;



// import React, { useEffect } from 'react';
// import { useNavigate } from 'react-router-dom';

// function Submitted({ images, setImages }) {
//   const navigate = useNavigate();

//   useEffect(() => {
//     const fetchImages = async () => {
//       const response = await fetch('http://localhost:8000/submitted');
//       const data = await response.json();
//       setImages(data);
//     }
//     fetchImages();
//   }, [setImages]);

//   const handleImageClick = (url) => {
//     navigate(`/improve/${encodeURIComponent(url)}`);
//   };
  
//   return (
//     <div className="container">
//       <h2>Submitted Images</h2>
//       {images.length === 0 ? (
//         <p>No images have been uploaded yet.</p>
//       ) : (
//         <div className="image-gallery">
//           {images.map((img, index) => (
//             <img 
//               key={index}
//               src={img.url}
//               alt={`Submitted ${index}`}
//               width="200"
//               onClick={() => handleImageClick(img.url)}
//               style={{ cursor: 'pointer' }}
//             />
//           ))}
//         </div>
//       )}
//     </div>
//   );
// }

// export default Submitted;
