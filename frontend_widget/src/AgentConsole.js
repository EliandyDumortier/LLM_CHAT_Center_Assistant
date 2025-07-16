import React, { useState, useEffect, useRef } from 'react';
import { User, Bot, Clock, Send, RefreshCw, MessageSquare } from 'lucide-react';

const AgentConsole = () => {
  const [pendingChats, setPendingChats] = useState([]);
  const [selectedChat, setSelectedChat] = useState(null);
  const [agentResponse, setAgentResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const intervalRef = useRef(null);

  const fetchPendingChats = async () => {
    try {
      const response = await fetch('http://localhost:8000/chat/pending');
      const data = await response.json();
      
      if (data.status === 'success') {
        setPendingChats(data.pending_chats);
      }
    } catch (error) {
      console.error('Error fetching pending chats:', error);
    }
  };

  const sendAgentResponse = async () => {
    if (!selectedChat || !agentResponse.trim()) return;

    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/chat/agent_respond', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: selectedChat.session_id,
          agent_response: agentResponse
        })
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        setAgentResponse('');
        setSelectedChat(null);
        fetchPendingChats();
      }
    } catch (error) {
      console.error('Error sending agent response:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPendingChats();
    
    if (autoRefresh) {
      intervalRef.current = setInterval(fetchPendingChats, 5000);
    }
    
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [autoRefresh]);

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-brand-dark">Agent Console</h1>
              <p className="text-brand-gray mt-1">Monitor and respond to customer chats</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="autoRefresh"
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                  className="text-brand-pink focus:ring-brand-pink"
                />
                <label htmlFor="autoRefresh" className="text-sm text-brand-gray">
                  Auto-refresh
                </label>
              </div>
              <button
                onClick={fetchPendingChats}
                className="flex items-center space-x-2 bg-brand-pink text-white px-4 py-2 rounded-lg hover:bg-opacity-90 transition-colors"
              >
                <RefreshCw size={16} />
                <span>Refresh</span>
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Pending Chats List */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm">
              <div className="p-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-brand-dark flex items-center">
                  <MessageSquare className="w-5 h-5 mr-2" />
                  Pending Chats ({pendingChats.length})
                </h2>
              </div>
              <div className="max-h-96 overflow-y-auto">
                {pendingChats.length === 0 ? (
                  <div className="p-4 text-center text-brand-gray">
                    <MessageSquare className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p>No pending chats</p>
                  </div>
                ) : (
                  pendingChats.map((chat) => (
                    <div
                      key={chat.session_id}
                      onClick={() => setSelectedChat(chat)}
                      className={`p-4 border-b border-gray-100 cursor-pointer hover:bg-gray-50 transition-colors ${
                        selectedChat?.session_id === chat.session_id ? 'bg-blue-50 border-blue-200' : ''
                      }`}
                    >
                      <div className="flex items-start space-x-3">
                        <div className="w-8 h-8 bg-brand-pink rounded-full flex items-center justify-center">
                          <User className="w-4 h-4 text-white" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <p className="text-sm font-medium text-brand-dark truncate">
                              {chat.user_id}
                            </p>
                            <div className="flex items-center text-xs text-brand-gray">
                              <Clock className="w-3 h-3 mr-1" />
                              {formatTime(chat.timestamp)}
                            </div>
                          </div>
                          <p className="text-sm text-brand-gray truncate mt-1">
                            {chat.latest_message}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Chat Details */}
          <div className="lg:col-span-2">
            {selectedChat ? (
              <div className="bg-white rounded-lg shadow-sm h-full">
                <div className="p-4 border-b border-gray-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-brand-dark">
                        Chat with {selectedChat.user_id}
                      </h3>
                      <p className="text-sm text-brand-gray">
                        Session: {selectedChat.session_id}
                      </p>
                    </div>
                    <div className="text-sm text-brand-gray">
                      {formatTime(selectedChat.timestamp)}
                    </div>
                  </div>
                </div>

                <div className="p-4 space-y-4">
                  {/* User Message */}
                  <div className="flex items-start space-x-3">
                    <div className="w-8 h-8 bg-brand-pink rounded-full flex items-center justify-center">
                      <User className="w-4 h-4 text-white" />
                    </div>
                    <div className="flex-1">
                      <div className="bg-gray-100 rounded-lg p-3">
                        <p className="text-sm text-brand-dark">
                          {selectedChat.latest_message}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* AI Response */}
                  <div className="flex items-start space-x-3">
                    <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                      <Bot className="w-4 h-4 text-white" />
                    </div>
                    <div className="flex-1">
                      <div className="bg-blue-50 rounded-lg p-3">
                        <p className="text-sm text-brand-dark">
                          {selectedChat.ai_response}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Agent Response Form */}
                  <div className="mt-6 p-4 bg-yellow-50 rounded-lg">
                    <h4 className="font-semibold text-brand-dark mb-3">
                      Agent Response
                    </h4>
                    <textarea
                      value={agentResponse}
                      onChange={(e) => setAgentResponse(e.target.value)}
                      placeholder="Type your response to the customer..."
                      rows={4}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-pink focus:border-transparent resize-none"
                    />
                    <div className="flex items-center justify-between mt-3">
                      <p className="text-sm text-brand-gray">
                        Review the AI response and provide additional assistance if needed
                      </p>
                      <button
                        onClick={sendAgentResponse}
                        disabled={isLoading || !agentResponse.trim()}
                        className="flex items-center space-x-2 bg-brand-pink text-white px-4 py-2 rounded-lg hover:bg-opacity-90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <Send size={16} />
                        <span>{isLoading ? 'Sending...' : 'Send Response'}</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-sm h-full flex items-center justify-center">
                <div className="text-center text-brand-gray">
                  <MessageSquare className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p className="text-lg">Select a chat to view details</p>
                  <p className="text-sm">Choose a pending chat from the list to respond</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentConsole;