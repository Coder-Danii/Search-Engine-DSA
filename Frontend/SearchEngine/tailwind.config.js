/** @type {import('tailwindcss').Config} */
export default {
    content: ['./index.html', './src/**/*.{js,jsx}'],
    darkMode: 'class',
    theme: {
        extend: {
            fontFamily: {
                poppins: ['Poppins', 'sans-serif'],
            },
            colors: {
                beige: {
                    100: '#F9F9F6',  // Lighter off-white, more towards grayish off-white
                    200: '#F2F2F0',  // Slightly darker but still very light
                    300: '#E5E5E2',  // A touch of gray to move away from yellowish tones
                },
                brown: {
                    700: '#5C4030',  // Slightly more muted, less saturated brown
                    800: '#4C3224',  // More matte brown, less saturated
                    900: '#3E271D',  // Dark brown with a matte feel
                },
            },
        },
    },
    plugins: [],
};
