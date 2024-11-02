import React, { useState, useRef } from 'react';

function Upload({ setImages }) {
  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  // const [uploadedURL, setUploadedURL] = useState(null);
  // const [initialPrompt, setInitialPrompt] = useState('');
  const fileInputRef = useRef(null);
  
  const handleImageChange = (event) => {
    const file = event.target.files[0];
    setImage(file);
    setImagePreview(URL.createObjectURL(file));
  };

  // const handlePromptChange = (event) => {
  //   setInitialPrompt(event.target.value);
  // };

  const handleUpload = async (event) => {
    event.preventDefault();
    const formData = new FormData();
    formData.append('image', image);
    // formData.append('initialPrompt', initialPrompt);

    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Upload failed.');

      const result = await response.json();
      alert(result.message);
      // setUploadedURL(result.url);

      setImage(null);
      setImagePreview(null);
      // setInitialPrompt('');
      fileInputRef.current.value = '';

      const imagesResponse = await fetch('http://localhost:8000/submitted');
      const imagesData = await imagesResponse.json();
      setImages(imagesData);

    } catch (error) {
      console.error('Error uploading image:', error);
      alert('Error uploading image. Please try again.');
    }
  };

  return (
    <div className="upload-container">
      <form onSubmit={handleUpload}>
        <div className="file-input-wrapper">
          <button
            type="button"
            className='custom-file-button'
            onClick={() => fileInputRef.current.click()}
          >
            Choose file
          </button>
          <input
            type="file"
            ref={fileInputRef}
            className='file-input'
            onChange={handleImageChange}
          />
          <span className="file-name">
            {image ? image.name : 'No file chosen'}
          </span>
        </div>
        <div className="preview-and-button">
          {imagePreview && (
            <img src={imagePreview} alt="Preview" />
          )}
          <button type="submit">Upload</button>
        </div>
      </form>
    </div>
  );
}

export default Upload;
