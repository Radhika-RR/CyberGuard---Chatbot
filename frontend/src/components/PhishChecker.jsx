/**
 * PhishChecker Component
 * Provides phishing detection interface with ML-powered analysis
 */

import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FaShieldAlt, 
  FaExclamationTriangle, 
  FaCheckCircle, 
  FaSpinner,
  FaCopy,
  FaTrash,
  FaEye,
  FaEyeSlash,
  FaInfoCircle
} from 'react-icons/fa';
import { phishingAPI, utils } from '../services/api';

const PhishChecker = () => {
  // State management
  const [inputText, setInputText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showFeatures, setShowFeatures] = useState(false);
  const [history, setHistory] = useState([]);
  const textareaRef = useRef(null);

  // Sample texts for demo
  const sampleTexts = {
    phishing: [
      "Urgent! Your account will be suspended unless you verify immediately at secure-bank-verify.com/update",
      "Congratulations! You've won $10,000! Click here to claim your prize now: winner-claim.net/prize",
      "Your PayPal account has been limited. Update your information at paypal-security-update.org immediately"
    ],
    legitimate: [
      "Thank you for your purchase. Your order #12345 will be delivered within 3-5 business days.",
      "Your appointment with Dr. Smith is confirmed for tomorrow at 2:00 PM. Please arrive 15 minutes early.",
      "Welcome to our newsletter! Here are this week's cybersecurity tips and best practices."
    ]
  };

  // Handle text analysis
  const analyzeText = async () => {
    if (!inputText.trim()) {
      setError('Please enter some text to analyze');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await phishingAPI.predict(inputText, true);
      setResult(response);
      
      // Add to history
      const historyItem = {
        id: Date.now(),
        text: inputText.substring(0, 100),
        result: response.prediction,
        confidence: response.confidence,
        timestamp: new Date().toLocaleString()
      };
      setHistory(prev => [historyItem, ...prev.slice(0, 9)]); // Keep last 10

    } catch (err) {
      setError(err.message || 'Failed to analyze text');
    } finally {
      setLoading(false);
    }
  };

  // Handle sample text selection
  const loadSample = (text) => {
    setInputText(text);
    setResult(null);
    setError(null);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  // Clear form
  const clearForm = () => {
    setInputText('');
    setResult(null);
    setError(null);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  // Copy to clipboard
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  // Get result styling
  const getResultStyling = (prediction, confidence) => {
    if (prediction === 'phishing') {
      return {
        bgColor: 'bg-red-50 border-red-200',
        textColor: 'text-red-800',
        icon: <FaExclamationTriangle className="text-red-600" />,
        label: 'PHISHING DETECTED'
      };
    } else if (prediction === 'legitimate') {
      return {
        bgColor: 'bg-green-50 border-green-200',
        textColor: 'text-green-800',
        icon: <FaCheckCircle className="text-green-600" />,
        label: 'APPEARS LEGITIMATE'
      };
    } else {
      return {
        bgColor: 'bg-gray-50 border-gray-200',
        textColor: 'text-gray-800',
        icon: <FaInfoCircle className="text-gray-600" />,
        label: 'UNCERTAIN'
      };
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <div className="flex justify-center items-center mb-4">
          <FaShieldAlt className="text-4xl text-blue-600 mr-3" />
          <h1 className="text-3xl font-bold text-gray-900">Phishing Detector</h1>
        </div>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          AI-powered phishing detection to analyze emails, messages, and URLs for potential threats
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Input Section */}
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="lg:col-span-2"
        >
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Analyze Text</h2>
              <div className="flex gap-2">
                <button
                  onClick={() => copyToClipboard(inputText)}
                  className="p-2 text-gray-500 hover:text-blue-600 transition-colors"
                  title="Copy text"
                  disabled={!inputText}
                >
                  <FaCopy />
                </button>
                <button
                  onClick={clearForm}
                  className="p-2 text-gray-500 hover:text-red-600 transition-colors"
                  title="Clear text"
                  disabled={!inputText}
                >
                  <FaTrash />
                </button>
              </div>
            </div>

            {/* Text Input */}
            <div className="mb-4">
              <textarea
                ref={textareaRef}
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Paste email content, message, or URL here..."
                className="w-full h-40 p-4 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                maxLength={10000}
              />
              <div className="flex justify-between items-center mt-2 text-sm text-gray-500">
                <span>{inputText.length}/10,000 characters</span>
                {inputText.length > 5000 && (
                  <span className="text-yellow-600">Large text may take longer to process</span>
                )}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 mb-4">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={analyzeText}
                disabled={loading || !inputText.trim()}
                className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <FaSpinner className="animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <FaShieldAlt />
                    Analyze for Phishing
                  </>
                )}
              </motion.button>
            </div>

            {/* Error Display */}
            <AnimatePresence>
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4"
                >
                  <div className="flex items-center gap-2 text-red-800">
                    <FaExclamationTriangle />
                    <span className="font-medium">Error:</span>
                    <span>{error}</span>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Results Display */}
            <AnimatePresence>
              {result && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="space-y-4"
                >
                  {/* Main Result */}
                  <div className={`rounded-lg p-6 border-2 ${getResultStyling(result.prediction).bgColor}`}>
                    <div className="flex items-center gap-3 mb-4">
                      {getResultStyling(result.prediction).icon}
                      <div>
                        <h3 className={`text-lg font-bold ${getResultStyling(result.prediction).textColor}`}>
                          {getResultStyling(result.prediction).label}
                        </h3>
                        <p className="text-sm text-gray-600">
                          Confidence: {utils.formatConfidence(result.confidence)}
                        </p>
                      </div>
                    </div>

                    {/* Probability Scores */}
                    <div className="grid grid-cols-2 gap-4 mb-4">
                      <div className="bg-white rounded-lg p-3">
                        <div className="text-sm text-gray-600 mb-1">Legitimate</div>
                        <div className="flex items-center gap-2">
                          <div className="flex-1 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-green-500 h-2 rounded-full transition-all duration-500"
                              style={{ width: `${result.probability.legitimate * 100}%` }}
                            ></div>
                          </div>
                          <span className="text-sm font-medium">
                            {utils.formatConfidence(result.probability.legitimate)}
                          </span>
                        </div>
                      </div>

                      <div className="bg-white rounded-lg p-3">
                        <div className="text-sm text-gray-600 mb-1">Phishing</div>
                        <div className="flex items-center gap-2">
                          <div className="flex-1 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-red-500 h-2 rounded-full transition-all duration-500"
                              style={{ width: `${result.probability.phishing * 100}%` }}
                            ></div>
                          </div>
                          <span className="text-sm font-medium">
                            {utils.formatConfidence(result.probability.phishing)}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Risk Level */}
                    <div className="bg-white rounded-lg p-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Risk Level:</span>
                        <span className={`font-medium capitalize ${utils.getRiskLevelColor(result.risk_level)}`}>
                          {result.risk_level?.replace('_', ' ')}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Feature Analysis Toggle */}
                  {result.features && (
                    <div className="bg-white rounded-lg border border-gray-200">
                      <button
                        onClick={() => setShowFeatures(!showFeatures)}
                        className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
                      >
                        <span className="font-medium text-gray-900">Feature Analysis</span>
                        {showFeatures ? <FaEyeSlash /> : <FaEye />}
                      </button>

                      <AnimatePresence>
                        {showFeatures && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            className="border-t border-gray-200 p-4 space-y-3"
                          >
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                              <div>
                                <span className="text-gray-600">URLs Found:</span>
                                <span className="ml-2 font-medium">{result.features.url_count}</span>
                              </div>
                              <div>
                                <span className="text-gray-600">Urgency Score:</span>
                                <span className="ml-2 font-medium">{result.features.urgency_score}</span>
                              </div>
                              <div>
                                <span className="text-gray-600">Threat Score:</span>
                                <span className="ml-2 font-medium">{result.features.threat_score}</span>
                              </div>
                              <div>
                                <span className="text-gray-600">Action Score:</span>
                                <span className="ml-2 font-medium">{result.features.action_score}</span>
                              </div>
                            </div>

                            {result.features.suspicious_domains?.length > 0 && (
                              <div>
                                <span className="text-sm text-gray-600">Suspicious Domains:</span>
                                <div className="mt-1 flex flex-wrap gap-2">
                                  {result.features.suspicious_domains.map((domain, index) => (
                                    <span key={index} className="bg-red-100 text-red-800 px-2 py-1 rounded text-sm">
                                      {domain}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}

                            <div className="bg-gray-50 rounded p-3">
                              <span className="text-sm text-gray-600">Overall Suspicion Score:</span>
                              <div className="flex items-center gap-2 mt-1">
                                <div className="flex-1 bg-gray-200 rounded-full h-2">
                                  <div 
                                    className="bg-gradient-to-r from-yellow-400 to-red-500 h-2 rounded-full transition-all duration-500"
                                    style={{ width: `${(result.features.suspicion_score || 0) * 100}%` }}
                                  ></div>
                                </div>
                                <span className="text-sm font-medium">
                                  {((result.features.suspicion_score || 0) * 100).toFixed(1)}%
                                </span>
                              </div>
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>

        {/* Sidebar */}
        <motion.div 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="space-y-6"
        >
          {/* Sample Texts */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Try Sample Texts</h3>
            
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-medium text-red-600 mb-2">⚠️ Phishing Examples</h4>
                <div className="space-y-2">
                  {sampleTexts.phishing.map((text, index) => (
                    <button
                      key={index}
                      onClick={() => loadSample(text)}
                      className="w-full text-left p-3 text-sm bg-red-50 hover:bg-red-100 rounded-lg transition-colors border border-red-200"
                    >
                      {utils.truncateText(text, 80)}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="text-sm font-medium text-green-600 mb-2">✅ Legitimate Examples</h4>
                <div className="space-y-2">
                  {sampleTexts.legitimate.map((text, index) => (
                    <button
                      key={index}
                      onClick={() => loadSample(text)}
                      className="w-full text-left p-3 text-sm bg-green-50 hover:bg-green-100 rounded-lg transition-colors border border-green-200"
                    >
                      {utils.truncateText(text, 80)}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Analysis History */}
          {history.length > 0 && (
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Recent Analysis</h3>
                <button
                  onClick={() => setHistory([])}
                  className="text-sm text-gray-500 hover:text-red-600"
                >
                  Clear
                </button>
              </div>
              
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {history.map((item) => (
                  <div key={item.id} className="border border-gray-200 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-1">
                      <span className={`text-xs font-medium uppercase ${
                        item.result === 'phishing' ? 'text-red-600' : 'text-green-600'
                      }`}>
                        {item.result}
                      </span>
                      <span className="text-xs text-gray-500">
                        {utils.formatConfidence(item.confidence)}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700 mb-1">
                      {item.text}...
                    </p>
                    <p className="text-xs text-gray-500">
                      {item.timestamp}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tips */}
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-200">
            <h3 className="text-lg font-semibold text-blue-900 mb-3">🛡️ Detection Tips</h3>
            <ul className="text-sm text-blue-800 space-y-2">
              <li>• Look for urgent language and time pressure</li>
              <li>• Check for suspicious URLs and domains</li>
              <li>• Be wary of unexpected money offers</li>
              <li>• Verify sender identity independently</li>
              <li>• Trust your instincts - if it feels wrong, it probably is</li>
            </ul>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default PhishChecker;