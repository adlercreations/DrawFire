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
