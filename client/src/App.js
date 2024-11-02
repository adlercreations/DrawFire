import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import Home from './components/Home';
import Upload from './components/Upload';
import Submitted from './components/Submitted';
import Improve from './components/Improve';
import './App.css';

function App() {
  const [images, setImages] = useState([]);
  return (
    <Router>
      <div className="header">
        <h1>🔥 DrawFire 🔥</h1>
        <nav>
          <Link to="/">Home</Link> | <Link to="/upload">Upload</Link> | 
          <Link to="/submitted">Submitted</Link> | 
          <Link to="/improve">Improve</Link>
        </nav>
      </div>
      <div className="sidebar-image sidebar-left"></div>
      <div className="sidebar-image sidebar-right"></div>
      <div className="main-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/upload" element={<Upload setImages={setImages} />} />
          <Route path="/submitted" element={<Submitted images={images} setImages={setImages} />} />
          <Route path="/improve" element={<Improve />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;



// import React, { useState } from 'react';
// import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
// import Home from './components/Home';
// import Upload from './components/Upload';
// import Submitted from './components/Submitted';
// import Improve from './components/Improve';
// import './App.css';

// function App() {
//   const [images, setImages] = useState([]);
//   return (
//     <Router>
//       <div className="header">
//         <h1>🔥 DrawFire 🔥</h1>
//         <nav>
//           <Link to="/">Home</Link> | <Link to="/upload">Upload</Link> | 
//           <Link to="/submitted">Submitted</Link> | 
//           <Link to="/improve">Improve</Link>
//         </nav>
//       </div>
//       <div className="main-content">
//         <Routes>
//           <Route path="/" element={<Home />} />
//           <Route path="/upload" element={<Upload setImages={setImages} />} />
//           <Route path="/submitted" element={<Submitted images={images} setImages={setImages} />} />
//           <Route path="/improve" element={<Improve />} />
//         </Routes>
//       </div>
//     </Router>
//   );
// }

// export default App;
