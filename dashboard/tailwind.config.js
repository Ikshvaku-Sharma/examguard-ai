/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        navy:     "#0D1B3E",
        darkBlue: "#102347",
        midBlue:  "#1A3A6B",
        accent:   "#00C6FF",
        cardBg:   "#132040",
        cardBg2:  "#172A4E",
      },
    },
  },
  plugins: [],
};
