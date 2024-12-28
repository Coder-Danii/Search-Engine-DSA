import { Search } from 'lucide-react';
import React, { useRef } from 'react';

export function SearchBar({ setSearchQuery, fetchResults, searchQuery, setQuery }) {
    const inputRef = useRef(null);

    const handleSearch = (e) => {
        e.preventDefault();  // Prevent the form default behavior (which could reset the form)
        if (searchQuery.trim()) {
            setSearchQuery(searchQuery);  // Trigger search with the query
            fetchResults(searchQuery);  // Trigger fetching results based on the query
        }
    };

    const handleChange = (e) => {
        setQuery(e.target.value);  // Update the searchQuery state on input change
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();  // Prevent default behavior for Enter key
            if (inputRef.current === document.activeElement) {
                handleSearch(e);  // Manually trigger search when Enter is pressed in the input
            }
        }
    };

    return (
        <form onSubmit={handleSearch} className="w-full max-w-2xl">
            <div className="flex items-center gap-2 bg-brown-800 dark:bg-beige-100 rounded-full overflow-hidden shadow-lg border border-brown-300 dark:border-brown-700">
                <input
                    ref={inputRef}
                    type="text"
                    value={searchQuery} // The searchQuery state should be passed down here
                    onChange={handleChange}  // Update the searchQuery state on user input
                    onKeyDown={handleKeyDown}  // Listen for keydown events
                    placeholder="Search anything, kiddo...."
                    className="flex-1 px-6 py-4 bg-transparent outline-none text-beige-100 dark:text-brown-800 placeholder:text-beige-200 dark:placeholder:text-brown-700"
                />
                <button
                    type="submit"
                    className="px-6 py-4 flex items-center gap-2 text-beige-100 dark:text-brown-800 hover:bg-brown-700 dark:hover:bg-beige-200 transition-colors"
                >
                    <Search size={20} />
                </button>
            </div>
        </form>
    );
}
