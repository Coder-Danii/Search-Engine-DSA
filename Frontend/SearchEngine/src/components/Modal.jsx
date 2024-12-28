import React, { useState, useEffect } from 'react';

export function Modal({ joke, onLike, onDislike, iconRef }) {
    const [modalPosition, setModalPosition] = useState({ left: 0, top: 0 });

    useEffect(() => {
        if (iconRef.current) {
            const iconRect = iconRef.current.getBoundingClientRect();
            setModalPosition({
                left: iconRect.left - 300, // Position modal to the left of the icon
                top: iconRect.top, // Align it vertically with the icon
            });
        }
    }, [iconRef]); // Run effect when iconRef changes

    return (
        <div
            className="absolute z-50 bg-white rounded-lg p-6 w-80 text-center shadow-lg"
            style={{
                left: '569px',
                padding: '10px',
                top: `${modalPosition.top}px`,
                transform: 'translateY(-50%)', // Adjust to center vertically around the icon
            }}
        >
            <p className="text-lg text-gray-700 mb-4">{joke}</p>
            <div className="flex justify-around">
                <button
                    className="px-4 py-2 bg-green-500 text-white rounded-full hover:bg-green-400"
                    onClick={onLike}
                >
                    Like
                </button>
                <button
                    className="px-4 py-2 bg-red-500 text-white rounded-full hover:bg-red-400"
                    onClick={onDislike}
                >
                    Dislike
                </button>
            </div>
        </div>
    );
}
