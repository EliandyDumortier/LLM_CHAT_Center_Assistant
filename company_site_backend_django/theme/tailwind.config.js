/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    // vos templates “propre à” l’app theme
    './templates/**/*.html',

    // le base.html de website
    '../website/templates/**/*.html',

    // tous les autres .html de website (ex. website/*.html)
    '../website/**/*.html',

    // vos JS qui génèrent peut-être des classnames
    './static_src/src/**/*.js',
  ],
  theme: {
    extend: {
      fontFamily: {
        inter: ['Inter', 'sans-serif'],
      },
      colors: {
        'brand-pink': '#FF385C',
        'brand-dark': '#222222',
        'brand-gray': '#717171',
        'brand-light': '#F7F7F7',
      },
      animation: {
        'fade-in': 'fadeIn 1s ease-out',
        bounce: 'bounce 2s infinite',
        pulse: 'pulse 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%':   { opacity: '0', transform: 'translateY(30px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
};
