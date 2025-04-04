import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

function UrlInputPage() {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [recentUrls, setRecentUrls] = useState([]);
  const [showRecent, setShowRecent] = useState(false);
  const navigate = useNavigate();
  const inputRef = useRef(null);
  const recentDropdownRef = useRef(null);

  // Load recent URLs from localStorage
  useEffect(() => {
    const savedUrls = localStorage.getItem('recentUrls');
    if (savedUrls) {
      try {
        setRecentUrls(JSON.parse(savedUrls).slice(0, 5));
      } catch (e) {
        console.error('Failed to parse recent URLs:', e);
      }
    }
    
    // Focus the input field on load
    inputRef.current?.focus();
    
    // Close dropdown when clicking outside
    const handleClickOutside = (event) => {
      if (recentDropdownRef.current && !recentDropdownRef.current.contains(event.target) && 
          inputRef.current && !inputRef.current.contains(event.target)) {
        setShowRecent(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Save URL to recent list
  const saveToRecent = (urlToSave) => {
    const updatedUrls = [
      urlToSave,
      ...recentUrls.filter(item => item !== urlToSave)
    ].slice(0, 5);
    
    setRecentUrls(updatedUrls);
    localStorage.setItem('recentUrls', JSON.stringify(updatedUrls));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    let urlToProcess = url.trim();
    
    // Basic URL validation
    if (!urlToProcess) {
      setError('Please enter a URL');
      inputRef.current?.focus();
      return;
    }
    
    // Add https:// if not present
    if (!/^https?:\/\//i.test(urlToProcess)) {
      urlToProcess = 'https://' + urlToProcess;
    }
    
    setIsLoading(true);
    setError('');
    
    try {
      // Make API call to your backend
      const response = await fetch('http://127.0.0.1:3000/api/process-url', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: urlToProcess }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to process URL');
      }
      
      const data = await response.json();
      
      // Save to recent URLs
      saveToRecent(urlToProcess);
      
      // Navigate to chat page with URL data
      navigate('/chat', { state: { urlData: data } });
    } catch (err) {
      setError(err.message || 'An error occurred processing this URL. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const selectRecentUrl = (selectedUrl) => {
    setUrl(selectedUrl);
    setShowRecent(false);
    inputRef.current?.focus();
  };

  const clearRecentUrls = () => {
    setRecentUrls([]);
    localStorage.removeItem('recentUrls');
    setShowRecent(false);
  };

  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 flex justify-between items-center">
          <h1 className="text-xl font-bold text-gray-900">
            <span className="text-blue-600">URL</span> Analyzer
          </h1>
          <div className="text-sm text-gray-500">
            Powered by AI
          </div>
        </div>
      </header>
      
      {/* Main content */}
      <main className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            {/* Card header */}
            <div className="bg-blue-600 px-6 py-4">
              <h2 className="text-xl font-semibold text-white">Analyze Any Website</h2>
              <p className="text-blue-100 text-sm mt-1">
                Enter a URL to start analyzing with AI
              </p>
            </div>
            
            {/* Card body */}
            <div className="p-6">
              <form onSubmit={handleSubmit} className="space-y-5">
                <div className="relative">
                  <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-1">
                    Website URL
                  </label>
                  <div className="relative">
                    <input
                      ref={inputRef}
                      type="text"
                      id="url"
                      value={url}
                      onChange={(e) => setUrl(e.target.value)}
                      onFocus={() => recentUrls.length > 0 && setShowRecent(true)}
                      placeholder="https://example.com"
                      className={`w-full pl-10 pr-4 py-3 border ${error ? 'border-red-300' : 'border-gray-300'} 
                                  rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                                  ${isLoading ? 'bg-gray-100' : 'bg-white'}`}
                      disabled={isLoading}
                    />
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M12.586 4.586a2 2 0 112.828 2.828l-3 3a2 2 0 01-2.828 0 1 1 0 00-1.414 1.414 4 4 0 005.656 0l3-3a4 4 0 00-5.656-5.656l-1.5 1.5a1 1 0 101.414 1.414l1.5-1.5zm-5 5a2 2 0 012.828 0 1 1 0 101.414-1.414 4 4 0 00-5.656 0l-3 3a4 4 0 105.656 5.656l1.5-1.5a1 1 0 10-1.414-1.414l-1.5 1.5a2 2 0 11-2.828-2.828l3-3z" clipRule="evenodd" />
                      </svg>
                    </div>
                    {recentUrls.length > 0 && showRecent && (
                      <div 
                        ref={recentDropdownRef}
                        className="absolute z-10 mt-1 w-full bg-white shadow-lg rounded-md border border-gray-200 overflow-hidden"
                      >
                        <div className="py-1">
                          <div className="px-3 py-2 text-xs font-medium text-gray-500 border-b border-gray-100 flex justify-between items-center">
                            <span>Recent URLs</span>
                            <button 
                              onClick={clearRecentUrls}
                              className="text-red-500 hover:text-red-700 text-xs"
                            >
                              Clear all
                            </button>
                          </div>
                          {recentUrls.map((recentUrl, index) => (
                            <button
                              key={index}
                              type="button"
                              onClick={() => selectRecentUrl(recentUrl)}
                              className="w-full text-left px-3 py-2 text-sm hover:bg-gray-100 truncate"
                            >
                              {recentUrl}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                  
                  {error && (
                    <div className="mt-2 text-sm text-red-600 flex items-center">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                      {error}
                    </div>
                  )}
                </div>
                
                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg shadow transition duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 flex justify-center items-center disabled:opacity-50"
                >
                  {isLoading ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Processing URL...
                    </>
                  ) : (
                    <>
                      Analyze Website
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 ml-1" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                    </>
                  )}
                </button>
              </form>
              
              {/* Feature highlights */}
              <div className="mt-6 pt-6 border-t border-gray-200">
                <h3 className="text-sm font-medium text-gray-700 mb-3">What you'll get:</h3>
                <div className="grid grid-cols-2 gap-3">
                  <div className="flex items-start">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-green-500 mr-2 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span className="text-sm text-gray-600">AI-powered summary</span>
                  </div>
                  <div className="flex items-start">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-green-500 mr-2 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span className="text-sm text-gray-600">Key topics extracted</span>
                  </div>
                  <div className="flex items-start">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-green-500 mr-2 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span className="text-sm text-gray-600">Interactive chat</span>
                  </div>
                  <div className="flex items-start">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-green-500 mr-2 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span className="text-sm text-gray-600">Content analysis</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div className="text-center mt-4 text-sm text-gray-500">
            Enter any website URL to analyze its content with AI
          </div>
        </div>
      </main>
      
      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-4">
        <div className="max-w-7xl mx-auto px-4 text-center text-sm text-gray-500">
          URL Analyzer &copy; {new Date().getFullYear()} • Built with AI-powered analysis
        </div>
      </footer>
    </div>
  );
}

export default UrlInputPage;