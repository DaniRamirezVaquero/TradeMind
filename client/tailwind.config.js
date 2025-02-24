// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      typography: {
        DEFAULT: {
          css: {
            color: '#fafafa', // color base del texto

            h1: {
              color: '#fafafa', // color de h1
              marginTop: '0',
            },
            h2: {
              color: '#fafafa', // color de h2
              marginTop: '0',
              marginBottom: '0.8rem'
            },
            h3: {
              color: '#fafafa', // color de h3
              marginTop: '1rem',
            },
            h4: {
              color: '#fafafa', // color de h4

            },
            strong: {
              color: '#fafafa', // color de strong
            },
            p: {
              color: '#fafafa', // color de p
            },
            ul: {
              marginTop: '0',
              margingBottom: '0',
            }
            // Puedes personalizar otros elementos como h3, p, li, etc.
          },
        },
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
}
