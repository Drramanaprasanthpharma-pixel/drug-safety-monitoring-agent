/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          950: '#0F1B2B',
          900: '#152437',
          700: '#2C4258',
          500: '#5A7085',
          300: '#9FB0BE',
          100: '#E4E9EC',
        },
        paper: '#FAFAF8',
        teal: {
          700: '#1E5757',
          600: '#2B6E6E',
          500: '#39898A',
          100: '#DCEBEA',
        },
        signal: {
          critical: '#8C1D18',
          high: '#B3261E',
          moderate: '#B7791F',
          low: '#3F7D45',
        },
      },
      fontFamily: {
        display: ['"Source Serif 4"', 'Georgia', 'serif'],
        body: ['"Inter"', 'system-ui', 'sans-serif'],
        data: ['"IBM Plex Mono"', 'ui-monospace', 'monospace'],
      },
    },
  },
  plugins: [],
}
