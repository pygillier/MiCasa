/** @type {import('tailwindcss').Config} */

const defaultTheme = require('tailwindcss/defaultTheme')

module.exports = {
  content: [
        './templates/**/*.html',
    ],
  theme: {
    backgroundColor: "#242B33",
    extend: {
      fontFamily: {
        'sans': ['"Amazon Ember"', ...defaultTheme.fontFamily.sans],
      },
      container: {
        center: true
      },
    },
  },
  plugins: [],
}
