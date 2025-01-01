/** @type {import('tailwindcss').Config} */

const defaultTheme = require('tailwindcss/defaultTheme')

module.exports = {
  content: [
      './templates/*.html',
      './templates/**/*.html',
    ],
  theme: {

    extend: {
      fontFamily: {
        'sans': ['"Amazon Ember"', ...defaultTheme.fontFamily.sans],
      },
      container: {
        center: true
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
