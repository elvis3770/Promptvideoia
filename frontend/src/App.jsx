import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import TextToVideo from './pages/TextToVideo';
import ImageToVideo from './pages/ImageToVideo';
import ReferenceImages from './pages/ReferenceImages';
import FirstLastFrames from './pages/FirstLastFrames';
import ExtendVideo from './pages/ExtendVideo';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<TextToVideo />} />
          <Route path="/image-to-video" element={<ImageToVideo />} />
          <Route path="/reference-images" element={<ReferenceImages />} />
          <Route path="/first-last" element={<FirstLastFrames />} />
          <Route path="/extend" element={<ExtendVideo />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
