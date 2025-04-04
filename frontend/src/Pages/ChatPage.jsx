import { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

function ChatPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const urlData = location.state?.urlData;

  // Check if we have URL data from the previous page
  useEffect(() => {
    if (!urlData) {
      // If no data, redirect back to the URL input page
      navigate('/');
      return;
    }
    
    // Add a welcome message with URL data and start auto-analysis
    setMessages([
      {
        role: 'system',
        content: `Analyzing website: ${urlData.analysis?.title || urlData.url || 'Unknown URL'}`,
        timestamp: new Date().toISOString(),
      },
    ]);
    
    // Auto-analyze the URL when first loading
    handleAutoAnalyze(urlData);
    
    // Focus the input field after analysis
    setTimeout(() => {
      inputRef.current?.focus();
    }, 1000);
  }, [location.state, navigate]);

  // Auto-analyze the URL
  const handleAutoAnalyze = async (urlData) => {
    if (isLoading) return;
    
    setIsLoading(true);
    
    try {
      const response = await fetch('http://127.0.0.1:3000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [{ role: 'user', content: 'Give me a summary of this website' }],
          url_data: urlData,
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to analyze URL');
      }
      
      const data = await response.json();
      
      // Add analysis response
      setMessages(prev => [
        ...prev,
        { 
          role: 'model', 
          content: data.message,
          timestamp: new Date().toISOString()
        }
      ]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        { 
          role: 'system', 
          content: 'Error: Failed to analyze website. Please try a different URL or try again later.',
          timestamp: new Date().toISOString()
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Auto-scroll to the bottom of the chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!input.trim() || isLoading) return;
    
    const userMessage = { 
      role: 'user', 
      content: input,
      timestamp: new Date().toISOString()
    };
    
    // Update messages with user input
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    
    try {
      // Make API call to your LLM backend
      const response = await fetch('http://127.0.0.1:3000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [...messages, userMessage],
          url_data: location.state?.urlData,
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to get response');
      }
      
      const data = await response.json();
      
      // Add assistant's response to the chat
      setMessages(prev => [...prev, { 
        role: 'model', 
        content: data.message,
        timestamp: new Date().toISOString()
      }]);
    } catch (err) {
      // Add error message
      setMessages(prev => [
        ...prev,
        { 
          role: 'system', 
          content: 'Error: Failed to get a response. Please try again.',
          timestamp: new Date().toISOString()
        },
      ]);
    } finally {
      setIsLoading(false);
      // Focus the input field after sending
      inputRef.current?.focus();
    }
  };

  const handleReset = () => {
    navigate('/');
  };
  
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };
  
  const toggleSidebar = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar with website info */}
      <div className={`bg-gray-800 text-white transition-all duration-300 overflow-hidden ${isExpanded ? 'w-72' : 'w-0 md:w-16'}`}>
        <div className="p-4">
          <button 
            onClick={toggleSidebar}
            className="flex items-center justify-center w-full mb-4"
          >
            <span className={`${isExpanded ? 'block' : 'hidden'} mr-2`}>Website Details</span>
            <svg xmlns="http://www.w3.org/2000/svg" className={`h-5 w-5 transition-transform ${isExpanded ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
          
          {isExpanded && urlData?.analysis && (
            <div className="space-y-4">
              <div>
                <h3 className="text-xs uppercase tracking-wider text-gray-400">Website</h3>
                <p className="text-sm truncate">{urlData.analysis.url}</p>
              </div>
              
              <div>
                <h3 className="text-xs uppercase tracking-wider text-gray-400">Title</h3>
                <p className="text-sm font-medium">{urlData.analysis.title || 'N/A'}</p>
              </div>
              
              <div>
                <h3 className="text-xs uppercase tracking-wider text-gray-400">Topic</h3>
                <p className="text-sm">{urlData.analysis.main_topic || 'N/A'}</p>
              </div>
              
              <div>
                <h3 className="text-xs uppercase tracking-wider text-gray-400">Key Points</h3>
                <ul className="text-sm list-disc pl-4 space-y-1">
                  {urlData.analysis.key_points?.slice(0, 10).map((point, idx) => (
                    <li key={idx} className="truncate">{point}</li>
                  ))}
                  {/* {urlData.analysis.key_points?.length > 3 && (
                    <li className="text-blue-300">+{urlData.analysis.key_points.length - 3} more</li>
                  )} */}
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Main chat area */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 shadow-sm">
          <div className="flex justify-between items-center px-4 py-3">
            <div className="flex items-center space-x-3">
              <button 
                onClick={toggleSidebar}
                className="md:hidden text-gray-600 hover:text-gray-900"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              <h1 className="text-lg font-semibold text-gray-800">
                <span className="text-blue-600">URL</span> Analyzer
              </h1>
            </div>
            <div className="flex items-center space-x-2">
              <div className="text-sm text-gray-500 hidden md:block">
                {urlData?.analysis?.url?.slice(0, 30)}{urlData?.analysis?.url?.length > 30 ? '...' : ''}
              </div>
              <button
                onClick={handleReset}
                className="px-3 py-1 bg-blue-600 text-white text-sm rounded-md 
                           hover:bg-blue-700 transition-colors duration-300 
                           focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
              >
                New URL
              </button>
            </div>
          </div>
        </header>
        
        {/* Chat messages area */}
        <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
          <div className="max-w-3xl mx-auto space-y-4">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`flex ${
                  msg.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`relative max-w-[80%] p-3 rounded-lg ${
                    msg.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : msg.role === 'system'
                      ? 'bg-gray-300 text-gray-800 text-center mx-auto max-w-md'
                      : 'bg-white text-gray-800 border border-gray-200 shadow-sm'
                  }`}
                >
                  {msg.role === 'model' && (
                    <div className="absolute -left-2 -top-2 w-6 h-6 rounded-full bg-blue-600 flex items-center justify-center text-white text-xs">
                      AI
                    </div>
                  )}
                  <div className="whitespace-pre-line">
                    {msg.content}
                  </div>
                  <div className={`text-xs mt-1 ${msg.role === 'user' ? 'text-blue-200' : 'text-gray-400'}`}>
                    {formatTimestamp(msg.timestamp)}
                  </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white border border-gray-200 p-4 rounded-lg shadow-sm max-w-[80%]">
                  <div className="flex space-x-2 items-center">
                    <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce delay-100"></div>
                    <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce delay-200"></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>
        
        {/* Input area */}
        <div className="border-t border-gray-200 bg-white p-4">
          <form onSubmit={handleSendMessage} className="max-w-3xl mx-auto flex items-center">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about this website..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="bg-blue-600 text-white px-6 py-3 rounded-r-md hover:bg-blue-700 transition-colors duration-300 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
            >
              <span className="hidden md:inline">Send</span>
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 md:hidden" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default ChatPage;