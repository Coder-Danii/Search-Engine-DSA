import axios from 'axios';
import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { AddDocumentModal } from '../components/AddDocumentModal';
import { ArticleList } from '../components/ArticleList';
import { Modal } from '../components/Modal';
import { MustacheIcon } from '../components/MustacheIcon';
import { Pagination } from '../components/Pagination';
import { SearchBar } from '../components/SearchBar';
import { SearchHeader } from '../components/SearchHeader';
import { SearchTags } from '../components/SearchTags';
import { SortOptions } from '../components/SortOptions';
import { jokes } from '../data/jokes';
import { cleanTag } from '../utils/stringUtils';

function useQuery() {
  return new URLSearchParams(useLocation().search);
}

function SearchResultsPage() {
  const [currentJoke, setCurrentJoke] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [tags, setTags] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTime, setSearchTime] = useState(null);
  const [currentSort, setCurrentSort] = useState('relevance');
  const itemsPerPage = 10;
  const navigate = useNavigate();
  const query = useQuery().get('q');

  const handleJokeClick = () => {
    const randomIndex = Math.floor(Math.random() * jokes.length);
    setCurrentJoke(jokes[randomIndex].joke);
    setIsModalOpen(true);
  };

  const sortResults = (results, sortType) => {
    switch (sortType) {
      case 'date':
        return [...results].sort((a, b) => 
          new Date(b.timestamp) - new Date(a.timestamp)
        );
      case 'alpha':
        return [...results].sort((a, b) => 
          a.title.localeCompare(b.title)
        );
      case 'relevance':
      default:
        return results;
    }
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
    setCurrentPage(1);

    const startTime = performance.now();

    try {
      const response = await axios.post('http://127.0.0.1:5000/search', {
        query: query,
        sort: currentSort
      });

      const endTime = performance.now();
      setSearchTime((endTime - startTime) / 1000);
      console.log(response.data);
      const data = response.data;
      if (!data.results || data.results.length === 0) {
        setError('No match found. We’re not perfect, but we’re getting there!');
        setSearchResults([]);
        setTags([]);
        setTotalPages(1);
      } else {
        setError('');
        const sortedResults = sortResults(data.results, currentSort);
        console.log(sortedResults);
        setSearchResults(sortedResults);
        setTotalPages(Math.ceil(sortedResults.length / itemsPerPage));

        const cleanedTags = data.tags.map(cleanTag);
        const tagCounts = cleanedTags.reduce((acc, tag) => {
          acc[tag] = (acc[tag] || 0) + 1;
          return acc;
        }, {});

        const sortedTags = Object.entries(tagCounts)
          .sort((a, b) => b[1] - a[1])
          .slice(0, 5)
          .map(([tag]) => tag);

        setTags(sortedTags);
      }
    } catch (err) {
      setError('Yikes! Our search skills are as "mid". Give it another go!');
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
  }, [query, currentSort]);

  const handleSearch = (newQuery) => {
    navigate(`/search?q=${encodeURIComponent(newQuery)}`);
    fetchResults(newQuery);
  };

  const handleTagClick = (tag) => {
    const cleanedTag = cleanTag(tag);
    setSearchQuery(cleanedTag);
    navigate(`/search?q=${encodeURIComponent(cleanedTag)}`);
    fetchResults(cleanedTag);
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
    window.scrollTo(0, 0);
  };

  const handleSortChange = (sortOption) => {
    setCurrentSort(sortOption);
    const sortedResults = sortResults(searchResults, sortOption);
    setSearchResults(sortedResults);
  };

  const handleAddDocument = () => {
    setIsAddModalOpen(true);
  };

  const handleAddSuccess = () => {
    // Refresh the search results if needed
    if (searchQuery) {
      fetchResults(searchQuery);
    }
  };

  const getCurrentPageResults = () => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return searchResults.slice(startIndex, endIndex);
  };

  return (
    <div className="min-h-screen bg-beige-100 dark:bg-brown-900 transition-colors">
      <div className="sticky top-0 z-40 bg-beige-100 dark:bg-brown-900 shadow-md">
        <div className="container mx-auto px-4 py-4">
          <SearchHeader title="mid." onAddDocument={handleAddDocument} />
          
          <div className="flex items-center justify-between mb-4">
            <h1 
              className="text-4xl font-bold text-brown-800 dark:text-beige-100 cursor-pointer" 
              onClick={() => navigate('/')}
            >
              mid.
            </h1>
            <div className="flex-grow mx-8 max-w-2xl">
              <SearchBar
                setSearchQuery={handleSearch}
                searchQuery={searchQuery}
                fetchResults={fetchResults}
                setQuery={setSearchQuery}
              />
            </div>
            <div
              className="w-12 h-12 rounded-full bg-brown-800 dark:bg-beige-100 flex items-center justify-center cursor-pointer"
              onClick={handleJokeClick}
            >
              <MustacheIcon className="w-8 h-8 text-beige-100 dark:text-brown-800" />
            </div>
          </div>

          <div className="flex items-center justify-between mt-4">
            <div className="flex items-center gap-4">
              {searchQuery && (
                <h2 className="text-xl text-brown-800 dark:text-beige-100">
                  Here are your average results for "{searchQuery}"
                </h2>
              )}
              {searchTime && (
                <span className="text-xs text-brown-600 dark:text-beige-400">
                  ({searchResults.length} results in {searchTime.toFixed(2)} seconds)
                </span>
              )}
            </div>
            <SortOptions currentSort={currentSort} onSortChange={handleSortChange} />
          </div>

          {tags.length > 0 && (
            <div className="mt-2">
              <SearchTags tags={tags} onTagClick={handleTagClick} />
            </div>
          )}
        </div>
      </div>

      <div className="container mx-auto px-4 py-4">
        {loading ? (
          <div className="flex justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brown-800 dark:border-beige-100"></div>
          </div>
        ) : error ? (
          <div className="text-center text-brown-800 dark:text-beige-100">{error}</div>
        ) : (
          <>
            <ArticleList articles={getCurrentPageResults()} />
            {searchResults.length > 0 && (
              <Pagination
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={handlePageChange}
              />
            )}
          </>
        )}
      </div>

      {isModalOpen && (
        <Modal
          joke={currentJoke}
          onLike={() => setIsModalOpen(false)}
          onDislike={() => setIsModalOpen(false)}
        />
      )}

      {isAddModalOpen && (
        <AddDocumentModal
          isOpen={isAddModalOpen}
          onClose={() => setIsAddModalOpen(false)}
          onSuccess={handleAddSuccess}
        />
      )}
    </div>
  );
}

export default SearchResultsPage;