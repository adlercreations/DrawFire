import React, { useEffect } from 'react';

function Submitted({ images, setImages }) {
  useEffect(() => {
    const fetchImages = async () => {
      const response = await fetch('http://localhost:8000/submitted');
      const data = await response.json();
      setImages(data);
    }
    fetchImages();
  }, [setImages]);
  
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
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default Submitted;
