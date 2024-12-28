import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Modal } from '../components/Modal'; // Import the Modal component
import { MustacheIcon } from '../components/MustacheIcon';
import { SearchBar } from '../components/SearchBar';
import { ThemeToggle } from '../components/ThemeToggle';
import { jokes } from '../data/jokes';

function HomePage() {
    const [currentJoke, setCurrentJoke] = useState('');
    const [isModalOpen, setIsModalOpen] = useState(false);
    const iconRef = useRef(null); // Reference for the icon
    const [searchQuery, setSearchQuery] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleJokeClick = () => {
        const randomIndex = Math.floor(Math.random() * jokes.length);
        setCurrentJoke(jokes[randomIndex].joke);
        setIsModalOpen(true); // Open the modal when a joke is selected
    };

    useEffect(() => {
        if (searchQuery.trim()) {
            navigate(`/search?q=${searchQuery}`);
        }
    }, [searchQuery, navigate]);

    const handleSearch = () => {
        if (!searchQuery.trim()) {
            setError('Please enter a valid search query.');
        } else {
            setError('');
            setSearchQuery(searchQuery);
        }
    };

    return (
        <div className="min-h-screen bg-beige-100 dark:bg-brown-900 transition-colors">
            <ThemeToggle />
            <div className="container mx-auto px-4 py-20">
                <div className="flex flex-col items-start gap-1 mb-8 ml-8" style={{ marginTop: '50px' }}>
                    {/* Text Section */}
                    <h1 className="text-6xl font-bold text-brown-800 dark:text-beige-100" style={{ marginLeft: '263px' }}>
                        mid.
                    </h1>
                    <p className="text-lg text-brown-600 dark:text-beige-300 italic" style={{ marginLeft: '266px' }}>
                        your average search engine
                    </p>
                </div>

                {/* Icon and Search Bar Section */}
                <div className="relative">
                    {/* Icon Section */}
                    <div
                        className="absolute right-4 -top-12 w-12 h-12 rounded-full bg-brown-800 dark:bg-beige-100 flex items-center justify-center"
                        style={{ marginTop: '-50px', marginRight: '284px' }}
                        onClick={handleJokeClick} // Add click handler
                        ref={iconRef} // Add ref to the icon
                    >
                        <MustacheIcon className="w-8 h-8 text-beige-100 dark:text-brown-800" />
                    </div>

                    {/* Search Bar */}
                    <div className="flex justify-center">
                        <SearchBar setSearchQuery={setSearchQuery} onSearch={handleSearch} />
                    </div>
                </div>

                {/* Modal for Joke Display */}
                {isModalOpen && (
                    <Modal
                        joke={currentJoke}
                        onLike={() => setIsModalOpen(false)}
                        onDislike={() => setIsModalOpen(false)}
                        iconRef={iconRef} // Pass the reference to Modal
                    />
                )}
            </div>
        </div>
    );
}

export default HomePage;
