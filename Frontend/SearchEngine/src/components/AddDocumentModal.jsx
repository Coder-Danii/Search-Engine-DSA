import React, { useState } from 'react';
import axios from 'axios';

export function AddDocumentModal({ isOpen, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    title: '',
    text: '',
    url: '',
    authors: '',
    timestamp: '',
    tags: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await axios.post('http://127.0.0.1:5000/addDocument', formData);
      if (response.status === 200) {
        onSuccess();
        onClose();
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to add document');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
  <div className="bg-white dark:bg-brown-800 rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
    <h2 className="text-2xl font-bold mb-4 text-brown-800 dark:text-beige-100">
      Add New Document
    </h2>
    
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-brown-600 dark:text-beige-300">
          Title
        </label>
        <input
          type="text"
          name="title"
          value={formData.title}
          onChange={handleChange}
          className="mt-1 w-full rounded-md border border-brown-300 p-2"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-brown-600 dark:text-beige-300">
          URL
        </label>
        <input
          type="url"
          name="url"
          value={formData.url}
          onChange={handleChange}
          className="mt-1 w-full rounded-md border border-brown-300 p-2"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-brown-600 dark:text-beige-300">
          Authors
        </label>
        <input
          type="text"
          name="authors"
          value={formData.authors}
          onChange={handleChange}
          className="mt-1 w-full rounded-md border border-brown-300 p-2"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-brown-600 dark:text-beige-300">
          Content
        </label>
        <textarea
          name="text"
          value={formData.text}
          onChange={handleChange}
          className="mt-1 w-full rounded-md border border-brown-300 p-2 h-32"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-brown-600 dark:text-beige-300">
          Tags (comma-separated)
        </label>
        <input
          type="text"
          name="tags"
          value={formData.tags}
          onChange={handleChange}
          className="mt-1 w-full rounded-md border border-brown-300 p-2"
          placeholder="e.g., technology, programming, web"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-brown-600 dark:text-beige-300">
          Timestamp
        </label>
        <input
          type="datetime-local"
          name="timestamp"
          value={formData.timestamp}
          onChange={handleChange}
          className="mt-1 w-full rounded-md border border-brown-300 p-2"
          required
        />
      </div>

      {error && (
        <div className="text-red-500 text-sm">{error}</div>
      )}

      <div className="flex justify-end space-x-4 mt-6">
        <button
          type="button"
          onClick={onClose}
          className="px-4 py-2 text-sm font-medium text-brown-600 hover:text-brown-800"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-brown-800 text-white rounded-md hover:bg-brown-700 disabled:opacity-50"
        >
          {loading ? 'Adding...' : 'Add Document'}
        </button>
      </div>
    </form>
  </div>
</div>
  );
}