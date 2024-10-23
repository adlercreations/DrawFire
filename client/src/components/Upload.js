import React, { useState } from 'react';

function Upload({ setImages }) {
  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);

  const handleUpload = async (event) => {
    event.preventDefault();
    const formData = new FormData();
    formData.append('image', image);

    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Upload failed.');

      const result = await response.json();
      alert(result.message);

      const imagesResponse = await fetch('http://localhost:8000/submitted');
      const imagesData = await imagesResponse.json();
      setImages(imagesData);

    } catch (error) {
      console.error('Error uploading image:', error);
      alert('Error uploading image. Please try again.');
    }
  };

  const handleImageChange = (event) => {
    const file = event.target.files[0];
    setImage(file);
    setImagePreview(URL.createObjectURL(file));
  };

  return (
    <div className="container">
      <form onSubmit={handleUpload}>
        <input type="file" onChange={handleImageChange} />
        {imagePreview && <img src={imagePreview} alt="Preview" width="200" />}
        <button type="submit">Upload</button>
      </form>
    </div>
  );
}

export default Upload;


// import React, { useState } from 'react';

// function Upload({ setImages }) {
//   const [image, setImage] = useState(null);
//   const [imagePreview, setImagePreview] = useState(null);

//   const handleUpload = async (event) => {
//     event.preventDefault();
//     const formData = new FormData();
//     formData.append('image', image);

//     try {
//       const response = await fetch('http://localhost:8000/upload', {
//         method: 'POST',
//         body: formData,
//       });

//       if (!response.ok) {
//         const errorText = await response.text();  // Capture error response
//         throw new Error(`Error: ${errorText}`);
//       }

//       const result = await response.json();
//       alert(result.message);
      
//       const imagesResponse = await fetch('http://localhost:8000/submitted');
//       const imagesData = await imagesResponse.json();
//       setImages(imagesData);

//     } catch (error) {
//       console.error('Error uploading image:', error);
//       alert('Error uploading image. Please try again.');
//     }
//   };


//   const handleImageChange = (event) => {
//     const file = event.target.files[0];
//     setImage(file);
//     setImagePreview(URL.createObjectURL(file));
//   };

//   return (
//     <div className="container">
//       <form onSubmit={handleUpload}>
//         <input type="file" onChange={handleImageChange} />
//         {imagePreview && <img src={imagePreview} alt="Preview" width="200" />}
//         <button type="submit">Upload</button>
//       </form>
//     </div>
//   );
// }

// export default Upload;
