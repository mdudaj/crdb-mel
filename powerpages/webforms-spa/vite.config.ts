import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    sourcemap: true,
    modulePreload: {
      resolveDependencies(_filename, deps) {
        return deps.filter((dep) => !dep.includes('vendor-datepicker-'));
      },
    },
    rollupOptions: {
      output: {
        entryFileNames: 'assets/[name]-[hash].mjs',
        chunkFileNames: 'assets/[name]-[hash].mjs',
        manualChunks(id) {
          if (id.includes('/node_modules/@vuepic/vue-datepicker/')) return 'vendor-datepicker';
          if (id.includes('/node_modules/@lucide/vue/')) return 'vendor-icons';
          if (id.includes('/node_modules/vue/')) return 'vendor-vue';
          return undefined;
        },
      },
    },
  },
});
