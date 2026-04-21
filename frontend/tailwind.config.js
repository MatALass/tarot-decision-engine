/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        surface: '#0b1020',
        panel: '#121a2e',
        border: '#23304f',
        accent: '#6ea8fe',
        success: '#28c76f',
        warning: '#ffb020',
      },
      boxShadow: {
        soft: '0 12px 40px rgba(0, 0, 0, 0.18)',
      },
    },
  },
  plugins: [],
}
