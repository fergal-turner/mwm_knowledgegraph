import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
    base: '/mwm_knowledgegraph/',
  plugins: [react()],
});