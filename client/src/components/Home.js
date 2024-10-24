import React from 'react';
import drawingFire from '../assets/drawing-fire.webp';
import '../Home.css';

function Home() {
  return (
    <div className="home-container">
      <h2>Welcome to DrawFire!</h2>
      <h3>Where you can learn to draw mo' fire.</h3>
      <img
        src={drawingFire}
        alt="drawing fire"
        className="home-image"
      />
      <p>Unleash your creativity and ignite your imagination!</p>
      <p>Upload an image to get started.</p>
    </div>
  );
}

export default Home;