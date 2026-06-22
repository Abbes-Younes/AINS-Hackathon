import React from 'react';

export const ScoresOverview = () => {
  return (
    <div className="card">
      <div className="card-header">
        <h2>Entrepreneurial Scores</h2>
        <button className="btn btn-secondary">View Details</button>
      </div>
      <div className="card-content">
        <div className="grid grid-3">
          <div className="score-card">
            <h3>Market Score</h3>
            <div className="score-value">68</div>
            <p>Below average - Room for improvement</p>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: '68%' }}></div>
            </div>
            <p className="text-muted">Customer validation, market size, competition</p>
          </div>

          <div className="score-card">
            <h3>Commercial Offer</h3>
            <div className="score-value">82</div>
            <p>Above average - Strong position</p>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: '82%' }}></div>
            </div>
            <p className="text-muted">Revenue model, pricing strategy, unit economics</p>
          </div>

          <div className="score-card">
            <h3>Innovation</h3>
            <div className="score-value">75</div>
            <p>Good - Solid foundation</p>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: '75%' }}></div>
            </div>
            <p className="text-muted">Technology readiness, IP protection, R&D efforts</p>
          </div>
        </div>

        <div className="grid grid-3" style={{ marginTop: '1.5rem' }}>
          <div className="score-card">
            <h3>Scalability</h3>
            <div className="score-value">61</div>
            <p>Below average - Needs attention</p>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: '61%' }}></div>
            </div>
            <p className="text-muted">Systems, processes, team structure, automation</p>
          </div>

          <div className="score-card">
            <h3>Growth Potential</h3>
            <div className="score-value">79</div>
            <p>Above average - Promising outlook</p>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: '79%' }}></div>
            </div>
            <p className="text-muted">Market expansion, partnerships, funding readiness</p>
          </div>

          <div className="score-card">
            <h3>Green/Sustainability</h3>
            <div className="score-value">54</div>
            <p>Below average - ESG opportunity</p>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: '54%' }}></div>
            </div>
            <p className="text-muted">Environmental impact, social responsibility, governance</p>
          </div>
        </div>
      </div>
    </div>
  );
};