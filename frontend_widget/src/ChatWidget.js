// src/ChatWidget.js
import React, { useState } from 'react';
import axios from 'axios';

export default function ChatWidget() {
  const [input, setInput] = useState('');
  const [suggestions, setSuggestions] = useState([]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    try {
      const res = await axios.post(
        'http://localhost:8000/chat/send',
        { user_id: 'u1', message: input },
        { headers: { 'Content-Type': 'application/json' } }
      );
      setSuggestions(res.data.suggestions);
    } catch (err) {
      console.error('API error', err);
    }
  };

  return (
    <div className="p-4 bg-white shadow-md rounded">
      <h3 className="text-lg mb-2">Chat with us</h3>
      <div className="flex mb-2">
        <input
          className="flex-1 border rounded px-2 py-1 mr-2"
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Type your question…"
          onKeyDown={e => e.key === 'Enter' && sendMessage()}
        />
        <button
          className="bg-blue-500 text-white px-4 rounded"
          onClick={sendMessage}
        >
          Send
        </button>
      </div>
      {suggestions.length > 0 && (
        <ul className="list-disc list-inside">
          {suggestions.map((s, i) => (
            <li key={i} className="mt-1">{s}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
