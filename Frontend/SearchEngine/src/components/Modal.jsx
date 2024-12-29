import React, { useEffect, useRef } from 'react';
import { X } from 'lucide-react';

export function Modal({ joke, onLike, onDislike, onClose, iconRef }) {
  const modalRef = useRef();

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (modalRef.current && !modalRef.current.contains(event.target)) {
        onClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [onClose]);

  const getModalPosition = () => {
    if (iconRef && iconRef.current) {
      const iconRect = iconRef.current.getBoundingClientRect();
      return {
        top: `${iconRect.top + window.scrollY}px`,
        left: `${iconRect.left - 280}px`, // Place the modal on the left side of the icon
      };
    }
    return {};
  };

  const playSound = (type) => {
    const soundPath =
      type === 'funny' ? '/public/happy.mp3' : '/public/sad.mp3';
    const audio = new Audio(soundPath);
    audio.play();
  };

  const handleLike = () => {
    playSound('funny');
    onLike();
  };

  const handleDislike = () => {
    playSound('notFunny');
    onDislike();
  };

  const modalPosition = getModalPosition();

  return (
    <div
      className="fixed z-50"
      style={modalPosition} // Dynamically position the modal
    >
      <div
        ref={modalRef}
        className="bg-white dark:bg-brown-800 rounded-lg p-4 shadow-lg w-64 relative"
      >
        <button
          onClick={onClose}
          className="absolute top-2 right-2 text-gray-500 hover:text-gray-700"
        >
          <X size={20} />
        </button>
        <p className="text-brown-800 dark:text-beige-100 text-sm mb-4">{joke}</p>
        <div className="flex justify-end gap-2">
          <button
            onClick={handleDislike}
            className="px-2 py-1 text-sm rounded bg-red-100 text-red-600 hover:bg-red-200"
          >
            Not Funny
          </button>
          <button
            onClick={handleLike}
            className="px-2 py-1 text-sm rounded bg-green-100 text-green-600 hover:bg-green-200"
          >
            Funny
          </button>
        </div>
      </div>
    </div>
  );
}
