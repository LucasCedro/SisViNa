/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{vue,js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: '#2C5530',
                secondary: '#4A7856',
                accent: '#7EA172',
                background: '#F5F7F6',
                text: '#2C3E50',
                success: '#4CAF50',
                info: '#2196F3',
                warning: '#FF9800',
            },
        },
    },
    plugins: [],
} 