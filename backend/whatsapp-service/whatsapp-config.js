require('dotenv').config({ path: '../.env' });

module.exports = {
  // Backend API configuration
  backendUrl: process.env.BACKEND_URL || 'http://127.0.0.1:8000',
  
  // Deadline detection keywords (case-insensitive)
  deadlineKeywords: [
    'deadline', 'due', 'submit', 'submission', 'assignment',
    'exam', 'test', 'quiz', 'project', 'presentation',
    'meeting', 'appointment', 'call', 'interview',
    'reminder', 'remember', 'don\'t forget', 'complete',
    'finish', 'deliver', 'send', 'upload', 'by', 'before',
    'tomorrow', 'today', 'tonight', 'this week', 'next week',
    'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
    'saturday', 'sunday', 'jan', 'feb', 'mar', 'apr', 'may',
    'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'
  ],
  
  // Chat filtering
  chatFilter: {
    // Monitor all chats by default
    monitorAll: true,
    
    // Specific chats to monitor (if monitorAll is false)
    whitelist: [],
    
    // Chats to ignore (even if monitorAll is true)
    blacklist: [
      // Add chat names to ignore, e.g., 'Spam Group'
    ],
    
    // Monitor group chats
    monitorGroups: true,
    
    // Monitor personal chats
    monitorPersonal: true
  },
  
  // Message filtering
  messageFilter: {
    // Minimum message length to process
    minLength: 10,
    
    // Maximum message length to process (avoid processing very long messages)
    maxLength: 500,
    
    // Ignore messages from yourself
    ignoreSelf: true,
    
    // Only process messages containing deadline keywords
    requireKeywords: true
  },
  
  // AI extraction settings
  extraction: {
    // Use AI for all messages with keywords
    useAI: true,
    
    // Confidence threshold (0-1) - not used yet, but planned
    confidenceThreshold: 0.7
  },
  
  // Logging
  logging: {
    // Log all messages (for debugging)
    logAllMessages: false,
    
    // Log only deadline detections
    logDeadlines: true,
    
    // Log errors
    logErrors: true
  }
};
