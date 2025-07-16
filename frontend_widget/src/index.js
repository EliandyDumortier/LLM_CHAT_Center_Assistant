import React from 'react';
import { createRoot } from 'react-dom/client';
import ChatWidget from './ChatWidget';
import './index.css';

// For embedding in Django
if (typeof window !== 'undefined') {
  window.ChatWidget = {
    init: function() {
      const container = document.getElementById('chat-widget');
      if (container) {
        const root = createRoot(container);
        root.render(<ChatWidget />);
      }
    },
    open: function() {
      // Dispatch custom event to open chat
      window.dispatchEvent(new CustomEvent('openChat'));
    }
  };
}

// For standalone development
if (process.env.NODE_ENV === 'development') {
  const container = document.getElementById('root');
  if (container) {
    const root = createRoot(container);
    root.render(<ChatWidget />);
  }
}