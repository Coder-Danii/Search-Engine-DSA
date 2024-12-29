import React from 'react';
import { SortAsc, Calendar, TrendingUp } from 'lucide-react';

export function SortOptions({ currentSort, onSortChange }) {
  const options = [
    { id: 'relevance', label: 'Relevance', icon: TrendingUp },
    { id: 'date', label: 'Date', icon: Calendar },
    { id: 'alpha', label: 'A-Z', icon: SortAsc },
  ];

  return (
    <div className="flex gap-2">
      {options.map(({ id, label, icon: Icon }) => (
        <button
          key={id}
          onClick={() => onSortChange(id)}
          className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm ${
            currentSort === id
              ? 'bg-brown-800 text-beige-100 dark:bg-beige-100 dark:text-brown-800'
              : 'bg-brown-100 text-brown-800 dark:bg-brown-800 dark:text-beige-100'
          }`}
        >
          <Icon size={14} />
          {label}
        </button>
      ))}
    </div>
  );
}