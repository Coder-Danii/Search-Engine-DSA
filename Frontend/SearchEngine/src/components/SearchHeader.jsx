import React from 'react';
import { Link } from 'react-router-dom';
import { MustacheIcon } from './MustacheIcon';
import { SearchBar } from './SearchBar';

export function SearchHeader() {
    return (
        <div className="flex items-center gap-6 mb-8">
            <Link to="/" className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-brown-800 dark:bg-beige-100 flex items-center justify-center">
                    <MustacheIcon className="w-5 h-5 text-beige-100 dark:text-brown-800" />
                </div>
                <span className="text-2xl font-bold text-brown-800 dark:text-beige-100">mid.</span>
            </Link>
            <div className="flex-1">
                <SearchBar />
            </div>
        </div>
    );
}