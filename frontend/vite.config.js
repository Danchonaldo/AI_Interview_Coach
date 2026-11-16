import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// The frontend calls /api/*; Vite proxies it to the FastAPI backend.
// No API keys ever live in the frontend.
const backend = process.env.VITE_BACKEND_URL || "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      "/api": { target: backend, changeOrigin: true, rewrite: (p) => p.replace(/^\/api/, "") },
    },
  },
});
