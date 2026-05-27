/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{vue,js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: {
                    50: '#EEF0EA',
                    100: '#CBD3C3',
                    200: '#A4B39A',
                    DEFAULT: '#596247',
                    600: '#47503A',
                    700: '#353D2B',
                    900: '#222A1C',
                },
                complement: {
                    dark: '#624E47',
                    light: '#F0EAE9',
                },
                analog: {
                    1: '#3E6247',
                    2: '#625947',
                },
                background: '#F5F4F2',
                surface: '#FFFFFF',
                text: {
                    primary: '#2C2D2A',
                    secondary: '#47503A',
                    muted: '#8E9089',
                },
                success: '#3E6247',
                error: '#8E3B2B',
                info: '#47607B',
                attention: '#C8A84B',
            },
            fontFamily: {
                sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
            },
        },
    },
    plugins: [],
}
