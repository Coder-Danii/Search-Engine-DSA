import React from 'react';
import { FilePlus } from 'lucide-react';
import { ThemeToggle } from './ThemeToggle';

export function SearchHeader({ title, onAddDocument }) {
  return (
    <div className="flex items-center justify-between px-4 py-2 bg-beige-100 dark:bg-brown-900">
      <ThemeToggle />
      <button
        onClick={onAddDocument}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-brown-800 text-beige-100 dark:bg-beige-100 dark:text-brown-800 hover:opacity-90"
      >
        <FilePlus size={16} />
        <span className="text-sm">Add Document</span>
      </button>
    </div>
  );
}