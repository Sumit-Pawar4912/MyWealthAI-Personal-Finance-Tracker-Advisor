import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { formatRupees } from '../utils/currency';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [userName, setUserName] = useState('User');
  const [copiedId, setCopiedId] = useState(null);
  const messagesEndRef = useRef(null);

  // Quick suggestions for users
  const quickSuggestions = [
    "How much did I spend this month?",
    "Show me my savings goals",
    "What's my total balance?",
    "Give me spending advice",
    "How much income did I earn?",
    "Analyze my spending patterns"
  ];

  // Scroll to bottom whenever messages change
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Fetch user profile on mount
  useEffect(() => {
    const fetchUserProfile = async () => {
      try {
        const token = localStorage.getItem('authToken');
        const response = await axios.get('http://localhost:5000/api/dashboard/profile', {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (response.data.user && response.data.user.first_name) {
          setUserName(response.data.user.first_name);
        }
      } catch (error) {
        console.error('Error fetching user profile:', error);
      }
    };

    fetchUserProfile();

    // Add initial greeting message
    setMessages([{
      id: 'initial',
      type: 'bot',
      text: `👋 Hello! I'm your AI Financial Assistant. I can help you with:
• 📊 Analyzing your spending and income
• 💡 Providing personalized financial advice
• 📈 Tracking your savings goals
• 💬 Answering questions about your finances

What would you like to know?`,
      timestamp: new Date()
    }]);
  }, []);

  const handleSendMessage = async (e) => {
    e.preventDefault();

    if (!inputValue.trim()) return;

    // Add user message to chat
    const userMessage = {
      id: Date.now(),
      type: 'user',
      text: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setLoading(true);

    try {
      const token = localStorage.getItem('authToken');
      const response = await axios.post(
        'http://localhost:5000/api/chatbot/message',
        { message: inputValue },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      if (response.data.success) {
        const botMessage = {
          id: `bot-${Date.now()}`,
          type: 'bot',
          text: response.data.response,
          intent: response.data.intent,
          timestamp: new Date(response.data.timestamp)
        };
        setMessages(prev => [...prev, botMessage]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: `error-${Date.now()}`,
        type: 'bot',
        text: '❌ Sorry, I encountered an error. Please try again later or contact support.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickSuggestion = (suggestion) => {
    setInputValue(suggestion);
  };

  const copyToClipboard = (text, messageId) => {
    navigator.clipboard.writeText(text);
    setCopiedId(messageId);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-700 via-blue-600 to-cyan-500 text-white p-6 shadow-2xl border-b border-blue-400">
        <div className="max-w-5xl mx-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="bg-white bg-opacity-20 backdrop-blur-sm rounded-full w-14 h-14 flex items-center justify-center text-3xl shadow-lg border border-white border-opacity-30">
                💬
              </div>
              <div>
                <h1 className="text-3xl font-bold tracking-tight">AI Financial Assistant</h1>
                <p className="text-blue-100 text-sm mt-1">💡 Your personal finance expert</p>
              </div>
            </div>
            <div className="hidden sm:block text-center">
              <div className="inline-block bg-white bg-opacity-10 backdrop-blur-sm rounded-lg px-4 py-2 border border-white border-opacity-20">
                <p className="text-sm font-medium">Ready to help</p>
                <p className="text-xs text-blue-100">Available 24/7</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 max-w-5xl mx-auto w-full">
        <div className="space-y-6">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'} animate-fadeIn`}
            >
              <div className={`group max-w-sm lg:max-w-md xl:max-w-lg`}>
                <div
                  className={`rounded-2xl p-4 shadow-lg transition-all duration-200 hover:shadow-xl ${
                    message.type === 'user'
                      ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-br-none border border-blue-500'
                      : 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white rounded-bl-none border border-slate-200 dark:border-slate-600'
                  }`}
                >
                  <div className="text-sm whitespace-pre-wrap break-words leading-relaxed">
                    {message.text.split('\n').map((line, idx) => (
                      <div key={idx}>{line}</div>
                    ))}
                  </div>
                  <div
                    className={`text-xs mt-3 pt-2 border-t ${
                      message.type === 'user'
                        ? 'text-blue-100 border-blue-500 border-opacity-30'
                        : 'text-slate-400 dark:text-slate-500 border-slate-200 dark:border-slate-600'
                    } flex justify-between items-center`}
                  >
                    <span>{formatTime(message.timestamp)}</span>
                    {message.type === 'bot' && (
                      <button
                        onClick={() => copyToClipboard(message.text, message.id)}
                        className={`ml-2 p-1 rounded transition-colors ${
                          copiedId === message.id
                            ? 'text-green-500 bg-green-50 dark:bg-green-900 dark:bg-opacity-30'
                            : 'text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-600'
                        }`}
                        title="Copy message"
                      >
                        {copiedId === message.id ? '✓' : '📋'}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-white dark:bg-slate-700 text-slate-900 dark:text-white border border-slate-200 dark:border-slate-600 rounded-2xl p-4 rounded-bl-none shadow-lg">
                <div className="flex gap-2">
                  <div className="w-3 h-3 bg-blue-400 rounded-full animate-bounce"></div>
                  <div className="w-3 h-3 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-3 h-3 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Quick Suggestions - Show if no messages beyond greeting */}
      {messages.length === 1 && !loading && (
        <div className="bg-slate-800 bg-opacity-50 backdrop-blur-sm border-t border-slate-700 px-6 py-4">
          <div className="max-w-5xl mx-auto">
            <p className="text-slate-300 text-sm font-medium mb-3">💡 Try asking:</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
              {quickSuggestions.map((suggestion, idx) => (
                <button
                  key={idx}
                  onClick={() => handleQuickSuggestion(suggestion)}
                  className="text-left text-sm p-3 bg-slate-700 hover:bg-slate-600 text-slate-100 rounded-lg transition-all duration-200 border border-slate-600 hover:border-blue-400 hover:shadow-lg"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="bg-slate-800 bg-opacity-70 backdrop-blur-lg border-t border-slate-700 p-4 shadow-2xl">
        <form onSubmit={handleSendMessage} className="max-w-5xl mx-auto">
          <div className="flex gap-3">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask me anything about your finances...✨"
              className="flex-1 px-5 py-3 bg-slate-700 text-white border border-slate-600 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder-slate-400 transition-all duration-200"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !inputValue.trim()}
              className="bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-700 hover:to-cyan-600 disabled:from-slate-500 disabled:to-slate-600 text-white font-semibold px-7 py-3 rounded-full transition-all duration-200 flex items-center gap-2 shadow-lg hover:shadow-xl disabled:shadow-none transform hover:scale-105 disabled:scale-100"
            >
              <span>Send</span>
              <span className="text-lg">📤</span>
            </button>
          </div>
        </form>
        <div className="max-w-5xl mx-auto mt-3 text-xs text-slate-400">
          💡 Tip: Ask about spending, income, savings, financial advice, or transaction analysis!
        </div>
      </div>

      {/* Add fade-in animation */}
      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }
      `}</style>
    </div>
  );
};

export default Chat;
