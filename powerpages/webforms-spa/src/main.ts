import { createApp } from 'vue';
import App from './App.vue';
import './styles.css';
import { logTimingHint, markTiming, measureTiming } from './performance';

const start = performance.now();
markTiming('spa-main-loaded');
logTimingHint();
const app = createApp(App);

if (import.meta.env.VITE_TACATDP_ODK_RUNTIME_ENABLED === 'false') {
  app.mount('#app');
  markTiming('app-mounted');
  measureTiming('app-mounted', start);
} else {
  try {
    const { webFormsPlugin } = await import('@getodk/web-forms');
    app.use(webFormsPlugin);
  } catch (error) {
    window.__TACATDP_ODK_PLUGIN_LOAD_ERROR__ = error instanceof Error ? error.message : String(error);
    console.error('[TACATDP] ODK runtime plugin failed to load. Shell will continue without collect runtime plugin.', error);
  }
  app.mount('#app');
  markTiming('app-mounted');
  measureTiming('app-mounted', start);
}
