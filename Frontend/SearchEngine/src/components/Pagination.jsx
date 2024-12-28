import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

export function Pagination({ currentPage, totalPages, onPageChange }) {
    return (
        <div className="flex justify-center items-center gap-4 mt-8 mb-6">
            <button
                onClick={() => onPageChange(currentPage - 1)}
                disabled={currentPage === 1}
                className="p-2 rounded-lg bg-brown-800 dark:bg-beige-100 text-beige-100 dark:text-brown-800 disabled:opacity-50"
            >
                <ChevronLeft size={20} />
            </button>

            <span className="text-brown-800 dark:text-beige-100">
                Page {currentPage} of {totalPages}
            </span>

            <button
                onClick={() => onPageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
                className="p-2 rounded-lg bg-brown-800 dark:bg-beige-100 text-beige-100 dark:text-brown-800 disabled:opacity-50"
            >
                <ChevronRight size={20} />
            </button>
        </div>
    );
}