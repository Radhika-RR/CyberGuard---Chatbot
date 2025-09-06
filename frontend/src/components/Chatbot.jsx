/**
 * Chatbot Component
 * AI-powered cybersecurity awareness chatbot with web search capabilities
 */

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FaRobot,
  FaUser,
  FaPaperPlane,
  FaSpinner,
  FaGlobe,
  FaBook,
  FaExternalLinkAlt,
  FaCopy,
  FaThumbsUp,
  FaThumbsDown,
  FaRefresh,
  FaBolt,
  FaLightbulb
} from 'react-icons/fa';
import { chatAPI, utils } from '../services/api';

const Chatbot = () => {
  // State management
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [searchMode, setSearchMode] = useState('web'); // 'web' or 'kb'
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Suggested questions
  const suggestedQuestions = [
    "How to detect phishing emails?",
    "What is two-factor authentication?",
    "How to create strong passwords?",
    "What should I do if I think I've been hacked?",
    "How to secure my WiFi network?",
    "What is social engineering?",
    "How to safely backup my data?",
    "What is a VPN and why should I use it?"
  ];

  // Initialize with welcome message
  useEffect(() => {
    const welcomeMessage = {
      id: Date.now(),
      type: 'bot',
      content: {
        summary: "👋 Hello! I'm your cybersecurity assistant. I can help you learn about online safety, detect threats, and answer your security questions. Ask me anything about cybersecurity!",
        sources: [],
        suggestions: suggestedQuestions.slice(0, 4)
      },
      timestamp: new Date()
    };
    setMessages([welcomeMessage]);
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Send message to chatbot
  const sendMessage = async (messageText = inputMessage) => {
    const trimmedMessage = messageText.trim();
    if (!trimmedMessage || loading) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: trimmedMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);
    setError(null);

    try {
      let response;
      if (searchMode === 'web') {
        response = await chatAPI.askWithWebSearch(trimmedMessage);
      } else {
        response = await chatAPI.askKnowledgeBase(trimmedMessage);
      }

      // Add bot response
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);

    } catch (err) {
      setError(err.message || 'Failed to get response');
      
      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: {
          summary: `Sorry, I encountered an error: ${err.message || 'Unknown error'}. Please try again or rephrase your question.`,
          sources: [],
          error: true
        },
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  // Handle Enter key press
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Copy message content
  const copyMessage = (content) => {
    const textToCopy = typeof content === 'string' ? content : content.summary;
    navigator.clipboard.writeText(textToCopy);
  };

  // Handle suggestion click
  const handleSuggestionClick = (suggestion) => {
    sendMessage(suggestion);
  };

  // Retry last message
  const retryLastMessage = () => {
    const lastUserMessage = [...messages].reverse().find(msg => msg.type === 'user');
    if (lastUserMessage) {
      sendMessage(lastUserMessage.content);
    }
  };

  // Clear chat
  const clearChat = () => {
    const welcomeMessage = {
      id: Date.now(),
      type: 'bot',
      content: {
        summary: "Chat cleared! How can I help you with cybersecurity today?",
        sources: [],
        suggestions: suggestedQuestions.slice(0, 4)
      },
      timestamp: new Date()
    };
    setMessages([welcomeMessage]);
    setError(null);
  };

  // Message component
  const Message = ({ message }) => {
    const isBot = message.type === 'bot';
    const isError = message.content.error;

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={`flex gap-3 ${isBot ? 'justify-start' : 'justify-end'} mb-6`}
      >
        {/* Avatar */}
        {isBot && (
          <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
            isError ? 'bg-red-100' : 'bg-blue-100'
          }`}>
            <FaRobot className={`text-sm ${isError ? 'text-red-600' : 'text-blue-600'}`} />
          </div>
        )}

        {/* Message Content */}
        <div className={`max-w-3xl ${isBot ? '' : 'order-first'}`}>
          <div className={`rounded-2xl p-4 ${
            isBot 
              ? isError 
                ? 'bg-red-50 border border-red-200' 
                : 'bg-white border border-gray-200 shadow-sm'
              : 'bg-blue-600 text-white'
          }`}>
            
            {/* User message - simple text */}
            {!isBot && (
              <p className="whitespace-pre-wrap break-words">{message.content}</p>
            )}

            {/* Bot message - complex content */}
            {isBot && (
              <div>
                {/* Main response */}
                <div className={`prose max-w-none ${isError ? 'text-red-800' : 'text-gray-800'}`}>
                  <p className="whitespace-pre-wrap break-words mb-0">
                    {message.content.summary}
                  </p>
                </div>

                {/* Sources */}
                {message.content.sources && message.content.sources.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="flex items-center gap-2 mb-2">
                      <FaGlobe className="text-sm text-gray-500" />
                      <span className="text-sm font-medium text-gray-700">Sources:</span>
                    </div>
                    <div className="space-y-2">
                      {message.content.sources.map((source, index) => (
                        <div key={index} className="bg-gray-50 rounded-lg p-3">
                          <div className="flex items-start gap-2">
                            <a
                              href={source.link}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="font-medium text-blue-600 hover:text-blue-800 flex items-center gap-1 flex-1"
                            >
                              {source.title}
                              <FaExternalLinkAlt className="text-xs" />
                            </a>
                          </div>
                          {source.snippet && (
                            <p className="text-sm text-gray-600 mt-1">
                              {utils.truncateText(source.snippet, 150)}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Suggestions */}
                {message.content.suggestions && message.content.suggestions.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="flex items-center gap-2 mb-2">
                      <FaLightbulb className="text-sm text-gray-500" />
                      <span className="text-sm font-medium text-gray-700">Related questions:</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {message.content.suggestions.slice(0, 3).map((suggestion, index) => (
                        <button
                          key={index}
                          onClick={() => handleSuggestionClick(suggestion)}
                          className="text-sm bg-blue-50 hover:bg-blue-100 text-blue-700 px-3 py-1 rounded-full transition-colors"
                          disabled={loading}
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Message actions */}
                <div className="flex items-center gap-2 mt-3 pt-3 border-t border-gray-100">
                  <button
                    onClick={() => copyMessage(message.content)}
                    className="text-xs text-gray-500 hover:text-blue-600 flex items-center gap-1"
                    title="Copy message"
                  >
                    <FaCopy />
                    Copy
                  </button>
                  
                  {searchMode === 'web' && (
                    <div className="flex items-center gap-1 text-xs text-gray-500">
                      <FaGlobe />
                      Web search
                    </div>
                  )}
                  
                  {searchMode === 'kb' && (
                    <div className="flex items-center gap-1 text-xs text-gray-500">
                      <FaBook />
                      Knowledge base
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Timestamp */}
          <div className={`text-xs text-gray-500 mt-1 ${isBot ? 'text-left' : 'text-right'}`}>
            {message.timestamp.toLocaleTimeString()}
          </div>
        </div>

        {/* User Avatar */}
        {!isBot && (
          <div className="flex-shrink-0 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
            <FaUser className="text-sm text-white" />
          </div>
        )}
      </motion.div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto p-6 h-screen flex flex-col">
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-6"
      >
        <div className="flex justify-center items-center mb-4">
          <FaRobot className="text-4xl text-blue-600 mr-3" />
          <h1 className="text-3xl font-bold text-gray-900">Cybersecurity Assistant</h1>
        </div>
        <p className="text-lg text-gray-600">
          Ask questions about online security, threats, and best practices
        </p>
      </motion.div>

      {/* Controls */}
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex items-center justify-between mb-6 p-4 bg-white rounded-xl shadow-sm border border-gray-200"
      >
        <div className="flex items-center gap-4">
          {/* Search Mode Toggle */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">Search with:</span>
            <div className="flex bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setSearchMode('web')}
                className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                  searchMode === 'web'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 hover:text-blue-600'
                }`}
              >
                <FaGlobe className="inline mr-1" />
                Web Search
              </button>
              <button
                onClick={() => setSearchMode('kb')}
                className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                  searchMode === 'kb'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 hover:text-blue-600'
                }`}
              >
                <FaBook className="inline mr-1" />
                Knowledge Base
              </button>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {error && (
            <button
              onClick={retryLastMessage}
              className="text-sm text-red-600 hover:text-red-800 flex items-center gap-1"
              title="Retry last message"
            >
              <FaRefresh />
              Retry
            </button>
          )}
          
          <button
            onClick={clearChat}
            className="text-sm text-gray-600 hover:text-red-600 flex items-center gap-1"
            title="Clear chat"
          >
            <FaRefresh />
            Clear
          </button>
        </div>
      </motion.div>

      {/* Messages Container */}
      <div className="flex-1 overflow-hidden flex flex-col">
        <div className="flex-1 overflow-y-auto px-4 py-2 space-y-4">
          <AnimatePresence>
            {messages.map((message) => (
              <Message key={message.id} message={message} />
            ))}
          </AnimatePresence>

          {/* Loading indicator */}
          {loading && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex gap-3 justify-start mb-6"
            >
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <FaRobot className="text-sm text-blue-600" />
              </div>
              <div className="bg-white border border-gray-200 rounded-2xl p-4 shadow-sm">
                <div className="flex items-center gap-2 text-gray-600">
                  <FaSpinner className="animate-spin" />
                  <span>
                    {searchMode === 'web' ? 'Searching the web...' : 'Thinking...'}
                  </span>
                </div>
              </div>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="border-t border-gray-200 p-4 bg-white"
        >
          {/* Quick suggestions (shown when no messages or conversation is short) */}
          {messages.length <= 1 && (
            <div className="mb-4">
              <div className="text-sm text-gray-600 mb-2">💡 Quick questions:</div>
              <div className="flex flex-wrap gap-2">
                {suggestedQuestions.slice(0, 6).map((question, index) => (
                  <button
                    key={index}
                    onClick={() => handleSuggestionClick(question)}
                    className="text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-2 rounded-lg transition-colors"
                    disabled={loading}
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input form */}
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <textarea
                ref={inputRef}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about cybersecurity, phishing, passwords, or any security topic..."
                className="w-full resize-none rounded-xl border border-gray-300 px-4 py-3 pr-12 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                rows={1}
                style={{
                  minHeight: '48px',
                  maxHeight: '120px',
                  height: 'auto'
                }}
                onInput={(e) => {
                  e.target.style.height = 'auto';
                  e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
                }}
                disabled={loading}
                maxLength={1000}
              />
              <div className="absolute right-3 bottom-3 text-xs text-gray-400">
                {inputMessage.length}/1000
              </div>
            </div>
            
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => sendMessage()}
              disabled={loading || !inputMessage.trim()}
              className="bg-blue-600 text-white p-3 rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center min-w-[48px]"
              title="Send message"
            >
              {loading ? (
                <FaSpinner className="animate-spin" />
              ) : (
                <FaPaperPlane />
              )}
            </motion.button>
          </div>

          {/* Hints */}
          <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
            <span>Press Enter to send, Shift+Enter for new line</span>
            <span className="flex items-center gap-1">
              <FaBolt className="text-yellow-500" />
              {searchMode === 'web' ? 'Real-time web results' : 'Instant knowledge base'}
            </span>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Chatbot;