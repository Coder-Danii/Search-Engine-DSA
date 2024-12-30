// src/App.js

import React from 'react';
import { Route, Routes } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import HomePage from './pages/HomePage';
import SearchResultsPage from './pages/SearchResultsPage';

function App() {
  return (
    <ThemeProvider>
              <h1 className='text-xl text-align-center text-[#fffff]'>Made by- Ali Aqdas</h1>

      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/search" element={<SearchResultsPage />} />
      </Routes>
    </ThemeProvider>
  );
}

export default App;
