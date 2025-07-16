import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ChatWidget from './ChatWidget';
import AgentConsole from './AgentConsole';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<ChatWidget />} />
          <Route path="/agent" element={<AgentConsole />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;