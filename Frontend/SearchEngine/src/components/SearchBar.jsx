import React, { useState, useEffect, useRef } from 'react';
import { Search } from 'lucide-react';

export function SearchBar({ setSearchQuery, searchQuery, fetchResults, setQuery, suggestions = [] }) {
  const [localQuery, setLocalQuery] = useState(searchQuery || '');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const suggestionsRef = useRef();

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (suggestionsRef.current && !suggestionsRef.current.contains(event.target)) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (setSearchQuery) {
      setSearchQuery(localQuery);
    }
    if (fetchResults) {
      fetchResults(localQuery);
    }
    setShowSuggestions(false);
  };

  const handleChange = (e) => {
    setLocalQuery(e.target.value);
    if (setQuery) {
      setQuery(e.target.value);
    }
    setShowSuggestions(true);
  };

  const handleSuggestionClick = (suggestion) => {
    setLocalQuery(suggestion);
    if (setSearchQuery) {
      setSearchQuery(suggestion);
    }
    if (fetchResults) {
      fetchResults(suggestion);
    }
    setShowSuggestions(false);
  };

  return (
    <div className="relative w-full" ref={suggestionsRef}>
      <form onSubmit={handleSubmit} className="w-full">
        <div className="relative">
        <input
  type="text"
  value={localQuery}
  onChange={handleChange}
  placeholder="Search..."
  className="w-full px-5 py-3 pl-16 rounded-full border-2 border-brown-300 dark:border-beige-700 bg-white dark:bg-brown-800 text-brown-900 dark:text-beige-100 focus:outline-none focus:ring-2 focus:ring-brown-500 dark:focus:ring-beige-500 transition-all ease-in-out duration-300"
  style={{
    transition: 'all 0.3s ease-in-out',
    borderRadius: '50px',
    borderColor: 'rgb(62, 39, 29)',
  }}
/>
<button type="submit" className="absolute left-4 top-1/2 -translate-y-1/2">
  <Search className="w-6 h-6 text-brown-400 dark:text-beige-400 transition-transform ease-in-out duration-200 hover:scale-110" />
</button>

        </div>
      </form>

      {showSuggestions && suggestions.length > 0 && (
        <div className="absolute w-full mt-1 bg-white dark:bg-brown-800 rounded-lg shadow-lg border border-brown-200 dark:border-brown-700 max-h-60 overflow-y-auto z-50">
          {suggestions.map((suggestion, index) => (
            <div
              key={index}
              className="px-4 py-2 hover:bg-brown-100 dark:hover:bg-brown-700 cursor-pointer text-brown-900 dark:text-beige-100"
              onClick={() => handleSuggestionClick(suggestion)}
            >
              {suggestion}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}