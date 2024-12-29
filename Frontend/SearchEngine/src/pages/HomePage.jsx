import React, { useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Modal } from '../components/Modal';
import { MustacheIcon } from '../components/MustacheIcon';
import { SearchBar } from '../components/SearchBar';
import { ThemeToggle } from '../components/ThemeToggle';
import { jokes } from '../data/jokes';

function HomePage() {
    const [currentJoke, setCurrentJoke] = useState('');
    const [isModalOpen, setIsModalOpen] = useState(false);
    const iconRef = useRef(null);
    const navigate = useNavigate();

    const handleJokeClick = () => {
        const randomIndex = Math.floor(Math.random() * jokes.length);
        setCurrentJoke(jokes[randomIndex].joke);
        setIsModalOpen(true);
    };

    const handleSearch = (query) => {
        if (query.trim()) {
            navigate(`/search?q=${encodeURIComponent(query)}`);
        }
    };

    return (
        <div className="min-h-screen bg-beige-100 dark:bg-brown-900 transition-colors">
            <ThemeToggle />
            <div className="container mx-auto px-4 flex flex-col justify-center min-h-screen">
                <div className="flex flex-col items-center gap-4 -mt-32">
                    <h1 className="text-6xl font-bold text-brown-800 dark:text-beige-100" style={{marginRight: "524px", marginBottom:"-10px"}}>
                        mid.
                    </h1>
                    <p className="text-lg text-brown-600 dark:text-beige-300 italic mb-8" style={{marginRight: "431px", marginBottom: "-1px"}}>
                        your average search engine
                    </p>

                    <div className="relative w-full max-w-2xl">
                        <SearchBar setSearchQuery={handleSearch} />
                        <div
                            className="absolute -right-16 top-1/2 -translate-y-1/2 w-12 h-12 rounded-full bg-brown-800 dark:bg-beige-100 flex items-center justify-center cursor-pointer" style={{marginTop:"-78px", marginRight:"70px"}}
                            onClick={handleJokeClick}
                            ref={iconRef}
                        >
                            <MustacheIcon className="w-8 h-8 text-beige-100 dark:text-brown-800" />
                        </div>
                    </div>
                </div>

                {isModalOpen && (
    <Modal
        joke={currentJoke}
        onLike={() => setIsModalOpen(false)}
        onDislike={() => setIsModalOpen(false)}
        onClose={() => setIsModalOpen(false)}
        iconRef={iconRef} // Pass the ref to the modal
    />
)}

            </div>
        </div>
    );
}

export default HomePage;