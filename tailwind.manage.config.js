/** @type {import('tailwindcss').Config} */

const defaultTheme = require('tailwindcss/defaultTheme')

module.exports = {
  content: [
      './templates/*.html',
      './templates/**/*.html',
      './node_modules/flowbite/**/*.js'
    ],
  theme: {
    extend: {
        colors: {
            'primary': {
                100: '#df4739',
                200: '#d65141',
                300: '#cd5949',
                400: '#c46150',
                500: '#ba6758',
                600: '#b06d60',
            },
            'surface': {
                100: '#f6f5f4',
                200: '#e8e7e6',
                300: '#dbdad9',
                400: '#cdcccc',
                500: '#c0bfbf',
                600: '#b3b2b2',
            },
            'tonal': {
                100: '#f8e5e0',
                200: '#ead9d5',
                300: '#dcceca',
                400: '#cfc2bf',
                500: '#c1b7b4',
                600: '#b4aca9',
            }
        },
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
      require('flowbite/plugin')
  ],
}
