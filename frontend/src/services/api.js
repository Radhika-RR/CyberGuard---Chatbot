/**
 * API Service Layer
 * Handles all HTTP requests to the CyberGuard Assistant backend
 */

import axios from 'axios';

// Base configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 second timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add timestamp to requests
    config.metadata = { startTime: new Date() };
    console.log(`🚀 ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    // Calculate request duration
    const duration = new Date() - response.config.metadata.startTime;
    console.log(`✅ ${response.config.method?.toUpperCase()} ${response.config.url} - ${response.status} (${duration}ms)`);
    return response;
  },
  (error) => {
    const duration = new Date() - error.config?.metadata?.startTime;
    console.error(`❌ ${error.config?.method?.toUpperCase()} ${error.config?.url} - ${error.response?.status} (${duration}ms)`);
    
    // Handle common error scenarios
    if (error.response?.status === 429) {
      throw new Error('Too many requests. Please wait a moment and try again.');
    }
    
    if (error.code === 'ECONNABORTED') {
      throw new Error('Request timed out. Please check your connection and try again.');
    }
    
    if (!error.response) {
      throw new Error('Network error. Please check your internet connection.');
    }
    
    return Promise.reject(error);
  }
);

/**
 * Phishing Detection API
 */
export const phishingAPI = {
  /**
   * Predict if text is phishing or legitimate
   * @param {string} text - Text to analyze
   * @param {boolean} includeFeatures - Whether to include feature analysis
   * @returns {Promise<Object>} Prediction result
   */
  async predict(text, includeFeatures = true) {
    try {
      const response = await api.post('/api/phish/predict', {
        text: text.trim(),
        include_features: includeFeatures
      });
      return response.data;
    } catch (error) {
      console.error('Phishing prediction error:', error);
      throw this.handleError(error);
    }
  },

  /**
   * Batch predict multiple texts
   * @param {string[]} texts - Array of texts to analyze
   * @param {boolean} includeFeatures - Whether to include feature analysis
   * @returns {Promise<Object>} Batch prediction results
   */
  async batchPredict(texts, includeFeatures = false) {
    try {
      const response = await api.post('/api/phish/batch', {
        texts: texts.map(t => t.trim()),
        include_features: includeFeatures
      });
      return response.data;
    } catch (error) {
      console.error('Batch prediction error:', error);
      throw this.handleError(error);
    }
  },

  handleError(error) {
    if (error.response?.data?.error) {
      return new Error(error.response.data.error);
    }
    return error;
  }
};

/**
 * Chatbot API
 */
export const chatAPI = {
  /**
   * Ask question using web search
   * @param {string} query - User question
   * @param {number} maxResults - Maximum search results
   * @returns {Promise<Object>} Chat response with sources
   */
  async askWithWebSearch(query, maxResults = 5) {
    try {
      const response = await api.post('/api/chat/web', {
        query: query.trim(),
        use_web_search: true,
        max_results: maxResults
      });
      return response.data;
    } catch (error) {
      console.error('Web search chat error:', error);
      throw this.handleError(error);
    }
  },

  /**
   * Ask question using knowledge base
   * @param {string} query - User question
   * @returns {Promise<Object>} Chat response from knowledge base
   */
  async askKnowledgeBase(query) {
    try {
      const response = await api.post('/api/chat/kb', {
        query: query.trim(),
        use_web_search: false
      });
      return response.data;
    } catch (error) {
      console.error('Knowledge base chat error:', error);
      throw this.handleError(error);
    }
  },

  handleError(error) {
    if (error.response?.data?.error) {
      return new Error(error.response.data.error);
    }
    return error;
  }
};

/**
 * System API
 */
export const systemAPI = {
  /**
   * Check API health status
   * @returns {Promise<Object>} Health check result
   */
  async getHealthStatus() {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      console.error('Health check error:', error);
      throw error;
    }
  },

  /**
   * Get API usage statistics
   * @returns {Promise<Object>} Usage statistics
   */
  async getStats() {
    try {
      const response = await api.get('/stats');
      return response.data;
    } catch (error) {
      console.error('Stats error:', error);
      throw error;
    }
  }
};

/**
 * Utility functions
 */
export const utils = {
  /**
   * Format confidence score as percentage
   * @param {number} confidence - Confidence score (0-1)
   * @returns {string} Formatted percentage
   */
  formatConfidence(confidence) {
    return `${(confidence * 100).toFixed(1)}%`;
  },

  /**
   * Get risk level color class
   * @param {string} riskLevel - Risk level
   * @returns {string} CSS color class
   */
  getRiskLevelColor(riskLevel) {
    const colors = {
      'very_low': 'text-green-600',
      'low': 'text-green-500',
      'medium': 'text-yellow-500',
      'high': 'text-red-500'
    };
    return colors[riskLevel] || 'text-gray-500';
  },

  /**
   * Get risk level background color
   * @param {string} riskLevel - Risk level
   * @returns {string} CSS background color class
   */
  getRiskLevelBg(riskLevel) {
    const colors = {
      'very_low': 'bg-green-100',
      'low': 'bg-green-50',
      'medium': 'bg-yellow-50',
      'high': 'bg-red-50'
    };
    return colors[riskLevel] || 'bg-gray-50';
  },

  /**
   * Truncate text with ellipsis
   * @param {string} text - Text to truncate
   * @param {number} maxLength - Maximum length
   * @returns {string} Truncated text
   */
  truncateText(text, maxLength = 100) {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  },

  /**
   * Format timestamp to readable date
   * @param {string} timestamp - ISO timestamp
   * @returns {string} Formatted date
   */
  formatTimestamp(timestamp) {
    try {
      return new Date(timestamp).toLocaleString();
    } catch (error) {
      return 'Invalid date';
    }
  },

  /**
   * Validate URL format
   * @param {string} url - URL to validate
   * @returns {boolean} Whether URL is valid
   */
  isValidUrl(url) {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  },

  /**
   * Extract domain from URL
   * @param {string} url - URL to extract domain from
   * @returns {string} Domain or original URL if invalid
   */
  extractDomain(url) {
    try {
      return new URL(url).hostname;
    } catch {
      return url;
    }
  },

  /**
   * Debounce function calls
   * @param {Function} func - Function to debounce
   * @param {number} wait - Wait time in milliseconds
   * @returns {Function} Debounced function
   */
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }
};

/**
 * Export all APIs as default object
 */
export default {
  phishing: phishingAPI,
  chat: chatAPI,
  system: systemAPI,
  utils
};