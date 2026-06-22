import React, { useState, useEffect } from 'react';

export const Scoring = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [scores, setScores] = useState<any>(null);

  useEffect(() => {
    // Simulate loading scores (in real app, this would come from backend)
    setLoading(true);

    // Simulate API call
    const timer = setTimeout(() => {
      setScores({
        overall: 71,
        market: 68,
        commercial_offer: 82,
        innovation: 75,
        scalability: 61,
        growth_potential: 79,
        green_sustainability: 54
      });
      setLoading(false);
    }, 1200);

    return () => clearTimeout(timer);
  }, []);

  if (loading) {
    return (
      <div className="app">
        <div className="main-content">
          <div className="container">
            <h1>Scoring Results</h1>
            <div className="card">
              <p>Loading your scores...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <div className="main-content">
        <div className="container">
          <h1>Scoring Results</h1>
          <p className="text-muted">Your entrepreneurial assessment scores with detailed breakdown</p>

          <div className="card">
            <div className="card-header">
              <h2>Overall Score</h2>
            </div>
            <div className="card-content">
              <div className="score-value" style={{ fontSize: '3rem', fontWeight: 'bold', textAlign: 'center' }}>
                {scores.overall}
              </div>
              <p className="text-center text-muted">out of 100</p>
              <div className="progress-bar" style={{ marginTop: '1rem' }}>
                <div className="progress-fill" style={{ width: `${scores.overall}%` }}></div>
              </div>
            </div>
          </div>

          <div className="card" style={{ marginTop: '1.5rem' }}>
            <div className="card-header">
              <h2>Score Breakdown</h2>
            </div>
            <div className="card-content">
              <div className="grid grid-3">
                <div className="score-detail">
                  <h3>Market</h3>
                  <div className="score-value-large">{scores.market}</div>
                  <p>Customer validation, market size, competition analysis</p>
                </div>
                <div className="score-detail">
                  <h3>Commercial Offer</h3>
                  <div className="score-value-large">{scores.commercial_offer}</div>
                  <p>Revenue model, pricing strategy, unit economics</p>
                </div>
                <div className="score-detail">
                  <h3>Innovation</h3>
                  <div className="score-value-large">{scores.innovation}</div>
                  <p>Technology readiness, IP protection, R&D efforts</p>
                </div>
              </div>

              <div className="grid grid-3" style={{ marginTop: '1.5rem' }}>
                <div className="score-detail">
                  <h3>Scalability</h3>
                  <div className="score-value-large">{scores.scalability}</div>
                  <p>Systems, processes, team structure, automation</p>
                </div>
                <div className="score-detail">
                  <h3>Growth Potential</h3>
                  <div className="score-value-large">{scores.growth_potential}</div>
                  <p>Market expansion, partnerships, funding readiness</p>
                </div>
                <div className="score-detail">
                  <h3>Green/Sustainability</h3>
                  <div className="score-value-large">{scores.green_sustainability}</div>
                  <p>Environmental impact, social responsibility, governance</p>
                </div>
              </div>
            </div>
          </div>

          <div className="card" style={{ marginTop: '1.5rem' }}>
            <div className="card-header">
              <h2>Score Interpretation</h2>
            </div>
            <div className="card-content">
              <div className="alert alert-info">
                <strong>Strengths:</strong> Strong commercial offer (82) and innovation (75) scores indicate a solid value proposition and technological foundation.
              </div>
              <div className="alert alert-warning" style={{ marginTop: '1rem' }}>
                <strong>Areas for Improvement:</strong> Market (68) and scalability (61) scores suggest need for better market validation and operational scaling capabilities.
              </div>
              <div className="alert alert-info" style={{ marginTop: '1rem' }}>
                <strong>Opportunity:</strong> Green/sustainability score (54) represents an opportunity to differentiate through ESG initiatives.
              </div>
            </div>
          </div>

          <div className="card" style={{ marginTop: '1.5rem' }}>
            <div className="card-header">
              <h2>Score History / Evolution</h2>
            </div>
            <div className="card-content">
              <p className="text-muted">Tracking your progress over time</p>
              <div className="card" style={{ padding: '1rem', backgroundColor: '#f8f9fa' }}>
                <p><strong>Latest Assessment:</strong> Today</p>
                <p><strong>Previous Assessment:</strong> Two weeks ago</p>
                <p><strong>Overall Score Change:</strong> ↑ +5 points</p>
                <p><strong>Biggest Improvement:</strong> Market score ↑ +6 points</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};