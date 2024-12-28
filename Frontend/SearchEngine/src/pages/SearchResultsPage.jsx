import axios from 'axios';
import React, { useEffect, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ArticleList } from '../components/ArticleList';
import { Modal } from '../components/Modal';
import { MustacheIcon } from '../components/MustacheIcon';
import { SearchBar } from '../components/SearchBar';
import { SearchTags } from '../components/SearchTags';
import { ThemeToggle } from '../components/ThemeToggle';
import { jokes } from '../data/jokes';

function useQuery() {
    return new URLSearchParams(useLocation().search);
}

function SearchResultsPage() {
    const [currentJoke, setCurrentJoke] = useState('');
    const [isModalOpen, setIsModalOpen] = useState(false);
    const iconRef = useRef(null);
    const [searchResults, setSearchResults] = useState([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [tags, setTags] = useState([]);
    const navigate = useNavigate();
    const query = useQuery().get('q');

    const handleJokeClick = () => {
        const randomIndex = Math.floor(Math.random() * jokes.length);
        setCurrentJoke(jokes[randomIndex].joke);
        setIsModalOpen(true);
    };

    const fetchResults = async (query) => {
        if (!query.trim()) {
            setError('Please enter a valid search query.');
            setSearchResults([]);
            setTags([]);
            return;
        }

        setLoading(true);
        setError('');
        setSearchResults([]);

        try {
            const response = await axios.post('http://127.0.0.1:5000/search', {
                query: query
            });
            if (response.data.results.length === 0) {
                setError('No results found.');
                setSearchResults([]);
                setTags([]);
            } else {
                setError('');
                setSearchResults(response.data.results);

                // Count tag frequencies
                const tagCounts = response.data.tags.reduce((acc, tag) => {
                    acc[tag] = (acc[tag] || 0) + 1;
                    return acc;
                }, {});

                // Get the top 5 most common tags
                const sortedTags = Object.entries(tagCounts)
                    .sort((a, b) => b[1] - a[1]) // Sort by frequency
                    .slice(0, 5) // Take the top 5
                    .map(([tag]) => tag); // Extract only tag names

                setTags(sortedTags);
            }
        } catch (err) {
            setError('An error occurred while fetching results.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (query) {
            setSearchQuery(query);
            fetchResults(query);
        }
    }, [query]);

    const handleSearch = (newQuery) => {
        // Make sure search query does not include a tag on Enter key press
        if (newQuery.trim() && !newQuery.includes(' ')) {
            navigate(`/search?q=${encodeURIComponent(newQuery)}`);
            fetchResults(newQuery);  // Fetch results based on the search query
        }
    };

    const handleTagClick = (tag) => {
        // Update search query by appending the tag, but prevent double-adding on Enter press
        const newQuery = searchQuery.trim()
            ? `${searchQuery} ${tag}`.trim()
            : tag;

        setSearchQuery(newQuery);
    };

    const handleLike = () => {
        const happySound = new Audio('/happy.mp3');
        happySound.play();
        setIsModalOpen(false);
    };

    const handleDislike = () => {
        const sadSound = new Audio('/sad.mp3');
        sadSound.play();
        setIsModalOpen(false);
    };

    return (
        <div className="min-h-screen bg-beige-100 dark:bg-brown-900 transition-colors">
            <ThemeToggle />
            <div className="container mx-auto px-4 py-20">
                <div className="flex flex-col items-start gap-1 mb-8 ml-8" style={{ marginTop: '50px' }}>
                    <h1 className="text-6xl font-bold text-brown-800 dark:text-beige-100" style={{ marginLeft: '263px' }}>
                        mid.
                    </h1>
                    <p className="text-lg text-brown-600 dark:text-beige-300 italic" style={{ marginLeft: '266px' }}>
                        your average search engine
                    </p>
                </div>

                <div className="relative">
                    <div
                        className="absolute right-4 -top-12 w-12 h-12 rounded-full bg-brown-800 dark:bg-beige-100 flex items-center justify-center"
                        style={{ marginTop: '-50px', marginRight: '284px' }}
                        onClick={handleJokeClick}
                        ref={iconRef}
                    >
                        <MustacheIcon className="w-8 h-8 text-beige-100 dark:text-brown-800" />
                    </div>

                    <div className="flex justify-center">
                        <SearchBar
                            setSearchQuery={handleSearch}
                            searchQuery={searchQuery}
                            fetchResults={fetchResults}
                            setQuery={setSearchQuery} // Pass setSearchQuery to update the state
                        />
                    </div>
                </div>

                {/* Display Search Tags */}
                {tags.length > 0 && <SearchTags tags={tags} onTagClick={handleTagClick} />}

                {/* Display Search Results */}
                <div>
                    {loading && <p>Loading...</p>}
                    {error && <p>{error}</p>}
                    <ArticleList articles={searchResults} />
                </div>

                {isModalOpen && (
                    <Modal
                        joke={currentJoke}
                        onLike={handleLike}
                        onDislike={handleDislike}
                        iconRef={iconRef}
                    />
                )}
            </div>
        </div>
    );
}

export default SearchResultsPage;
