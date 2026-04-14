/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        osin: {
          emerald: "#10b981",
          cyan: "#22d3ee",
          purple: "#a855f7",
          black: "#000000",
          gray: "#111827",
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
        orbitron: ['Orbitron', 'sans-serif'],
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow-cyan': 'glowCyan 2s ease-in-out infinite alternate',
        'glow-emerald': 'glowEmerald 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glowCyan: {
          'from': { boxShadow: '0 0 5px #22d3ee, 0 0 10px #22d3ee' },
          'to': { boxShadow: '0 0 20px #22d3ee, 0 0 30px #22d3ee' },
        },
        glowEmerald: {
          'from': { boxShadow: '0 0 5px #10b981, 0 0 10px #10b981' },
          'to': { boxShadow: '0 0 20px #10b981, 0 0 30px #10b981' },
        }
      }
    },
  },
  plugins: [],
}
