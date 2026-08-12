/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#080b11',
        surface: {
          DEFAULT: '#0f172a',
          hover: '#1e293b',
          card: 'rgba(15, 23, 42, 0.75)',
          glass: 'rgba(15, 23, 42, 0.65)',
        },
        brand: {
          cyan: '#00f0ff',
          blue: '#0088ff',
          glow: '#00f0ff40',
        },
        risk: {
          low: '#10b981',      // Safe (Green)
          medium: '#eab308',   // Moderate (Yellow)
          high: '#f97316',     // High (Orange)
          critical: '#ef4444', // Critical (Red)
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow-pulse': 'glowPulse 2s ease-in-out infinite alternate',
        'radar-sweep': 'radarSweep 4s linear infinite',
      },
      keyframes: {
        glowPulse: {
          '0%': { boxShadow: '0 0 5px rgba(0, 240, 255, 0.4), inset 0 0 5px rgba(0, 240, 255, 0.2)' },
          '100%': { boxShadow: '0 0 20px rgba(0, 240, 255, 0.8), inset 0 0 10px rgba(0, 240, 255, 0.4)' },
        },
        radarSweep: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        }
      }
    },
  },
  plugins: [],
}
