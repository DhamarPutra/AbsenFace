import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import AddMahasiswa from './pages/addMahasiswa';
import Scan from './pages/scan';

const App = () => {
  return (
    <Router>
      <div>
        <Routes>
          <Route path="/addMahasiswa" exact element={<AddMahasiswa/>} />
          <Route path="/scanAbsen" element={<Scan/>} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
