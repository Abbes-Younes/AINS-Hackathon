import React, { useState } from 'react';

export const Assistant = () => {
  const [messages, setMessages] = useState<Array<{id: number; text: string; isUser: boolean}>>([]);
  const [input, setInput] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  // Initialize with a welcome message
  React.useEffect(() => {
    setMessages([
      {
        id: 1,
        text: "Hello! I'm your entrepreneurial assistant. I can help you understand your diagnostic results, scores, and recommend specific actions based on your profile. How can I assist you today?",
        isUser: false
      }
    ]);
  }, []);

  const sendMessage = async () => {
    if (input.trim() === '') return;

    const userMessage = {
      id: Date.now(),
      text: input,
      isUser: true
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    // Simulate API call to backend
    try {
      // Simulate delay
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Generate a mock response based on the user's message
      let botResponse = "I'm here to help! Based on your entrepreneurial profile, I can provide guidance on your diagnostic results, scores, and recommended next steps.";

      // Simple keyword matching for demo purposes
      const lowerInput = input.toLowerCase();
      if (lowerInput.includes('score') || lowerInput.includes('market') || lowerInput.includes('commercial')) {
        botResponse = "Looking at your scores, I notice your Market Score is 68 and Commercial Offer Score is 82. Your commercial offer is strong, but market validation could be improved. I recommend completing the BFPME pre-financing guide to strengthen your financial documentation.";
      } else if (lowerInput.includes('roadmap') || lowerInput.includes('action') || lowerInput.includes('next')) {
        botResponse = "Based on your current stage and identified blockers, your immediate next steps should be: 1) Complete financial documentation using the BFPME template, 2) Formalize your legal structure through ANPE registration. These actions will resolve your highest priority blockers.";
      } else if (lowerInput.includes('diagnostic') || lowerInput.includes('stage') || lowerInput.includes('gap')) {
        botResponse = "Your diagnostic shows you're in the Structuration stage with an over-estimation perception gap (you see yourself at Fundraising, but evidence places you at Structuration). This suggests you should focus on gathering more evidence before pursuing financing.";
      } else if (lowerInput.includes('blocker') || lowerInput.includes('barrier')) {
        botResponse = "Your priority blockers are: 1) Financial Documentation (high priority) - missing detailed financial projections, and 2) Legal Structure (medium priority) - business not yet registered as a formal legal entity. Addressing these will significantly improve your readiness for financing.";
      } else if (lowerInput.includes('resource') || lowerInput.includes('program') || lowerInput.includes('funding')) {
        botResponse = "For your current situation, I recommend: 1) Startup Act Labellisation for access to public financing, 2) BFPME Pre-Financing Guide for financial documentation, and 3) ANPE Business Registration Portal for legal formalization. These resources directly address your identified gaps.";
      }

      const botMessage = {
        id: Date.now() + 1,
        text: botResponse,
        isUser: false
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        text: "Sorry, I encountered an error processing your request. Please try again.",
        isUser: false
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  return (
    <div className="app">
      <div className="main-content">
        <div className="container">
          <h1>Entrepreneurial Assistant</h1>
          <p className="text-muted">Get personalized guidance based on your diagnostic and scoring results</p>
          <p className="text-muted small">*This assistant is grounded in your specific entrepreneurial profile and references real Tunisian resources*</p>

          <div className="card" style={{ height: '600px', display: 'flex', flexDirection: 'column' }}>
            <div className="chat-messages" style={{ flex: 1, overflowY: 'auto', padding: '1rem' }}>
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`chat-message ${msg.isUser ? 'user' : 'bot'}`}
                >
                  <div className="chat-message-content">{msg.text}</div>
                </div>
              ))}
              {loading && (
                <div className="chat-message bot">
                  <div className="chat-message-content">Thinking...</div>
                </div>
              )}
            </div>
            <div className="chat-input">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me about your diagnostic, scores, roadmap, or resources..."
                className="form-control"
                disabled={loading}
              />
              <button
                onClick={sendMessage}
                disabled={loading || input.trim() === ''}
                className="btn btn-primary"
              >
                {loading ? 'Sending...' : 'Send'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};