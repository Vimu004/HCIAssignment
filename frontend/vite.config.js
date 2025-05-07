import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    outDir: '../static/js',
    emptyOutDir: true,
    rollupOptions: {
      input: './main.js'
    }
  }
});
