/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        surface:  '#08090d',
        deep:     '#0c0e16',
        panel:    '#10131f',
        card:     '#141828',
        border:   '#1e2538',
        rim:      '#2a3350',
        gold:     '#c9963a',
        'gold-light': '#e8b55a',
        'gold-dim':   '#7a5a22',
        amber:    '#f0a830',
        ruby:     '#c0374a',
        emerald:  '#2aab6f',
        sapphire: '#3a78c9',
        muted:    '#4a5578',
        text:     '#d8ddf0',
        subtle:   '#6b7899',
      },
      fontFamily: {
        display: ['Cinzel', 'Georgia', 'serif'],
        body:    ['"DM Sans"', 'system-ui', 'sans-serif'],
        mono:    ['"JetBrains Mono"', 'monospace'],
      },
      boxShadow: {
        'glow-gold': '0 0 20px rgba(201,150,58,0.15), 0 0 60px rgba(201,150,58,0.05)',
        'glow-ruby': '0 0 20px rgba(192,55,74,0.2)',
        'glow-emerald': '0 0 20px rgba(42,171,111,0.2)',
        'inner-panel': 'inset 0 1px 0 rgba(255,255,255,0.04)',
        'card-float': '0 8px 32px rgba(0,0,0,0.5), 0 2px 8px rgba(0,0,0,0.3)',
        'soft': '0 16px 48px rgba(0,0,0,0.4)',
      },
      backgroundImage: {
        'gold-gradient': 'linear-gradient(135deg, #c9963a 0%, #e8b55a 50%, #c9963a 100%)',
        'panel-gradient': 'linear-gradient(160deg, #10131f 0%, #0c0e16 100%)',
        'surface-gradient': 'radial-gradient(ellipse at 30% 0%, #13172a 0%, #08090d 60%)',
      },
      keyframes: {
        'shimmer': {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        'slide-up': {
          from: { opacity: '0', transform: 'translateY(10px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        'fade-in': {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
      },
      animation: {
        'shimmer': 'shimmer 2s linear infinite',
        'slide-up': 'slide-up 0.3s ease-out',
        'fade-in': 'fade-in 0.4s ease-out',
      },
    },
  },
  plugins: [],
}
