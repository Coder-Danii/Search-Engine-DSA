import { Tag } from 'lucide-react';
import React from 'react';

export function SearchTags({ tags, onTagClick }) {
    return (
        <div className="flex flex-wrap gap-2 mb-8">
            {tags.map((tag, index) => (
                <span
                    key={index}
                    className="flex items-center gap-1 px-3 py-1 rounded-full bg-brown-800 dark:bg-beige-100 text-beige-100 dark:text-brown-800 hover:bg-brown-700 dark:hover:bg-beige-200 cursor-pointer"
                    onClick={() => onTagClick(tag)} // Call onTagClick when a tag is clicked
                >
                    <Tag size={14} />
                    <span className="text-sm font-medium">{tag}</span>
                </span>
            ))}
        </div>
    );
}
