import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    // [FLOWFORGE ERROR 2: Build Configuration ReferenceError]
    // To disable this error, comment out or remove the line below:
    flowForgeOptimizerPlugin(),
  ],
})