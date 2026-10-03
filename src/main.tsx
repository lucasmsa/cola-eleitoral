import '@fontsource/bitter/latin-400.css';
import '@fontsource/bitter/latin-600.css';
import '@fontsource/bitter/latin-700.css';
import '@fontsource/bitter/latin-800.css';
import './styles/index.css';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { inject } from '@vercel/analytics';
import { App } from './components/App';

// Page views only, same-origin (/_vercel/insights); answers never leave the browser.
if (import.meta.env.PROD) inject({ mode: 'production' });

createRoot(document.getElementById('root') as HTMLElement).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
