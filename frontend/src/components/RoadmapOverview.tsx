import React from 'react';

export const RoadmapOverview = () => {
  return (
    <div className="card">
      <div className="card-header">
        <h2>Personalized Roadmap</h2>
        <button className="btn btn-secondary">View Full Roadmap</button>
      </div>
      <div className="card-content">
        <div className="timeline">
          <div className="timeline-item active">
            <div className="timeline-content">
              <h3>Immediate (0-30 days)</h3>
              <p><strong>Complete Financial Documentation Package</strong></p>
              <p>Use BFPME pre-financing template to create detailed financial projections</p>
              <p className="text-muted">Effort: High | Impact: High</p>
            </div>
          </div>

          <div className="timeline-item">
            <div className="timeline-content">
              <h3>Short-term (1-3 months)</h3>
              <p><strong>Formalize Legal Structure</strong></p>
              <p>Register business as SARL through ANPE portal</p>
              <p className="text-muted">Effort: Medium | Impact: High</p>
            </div>
          </div>

          <div className="timeline-item">
            <div className="timeline-content">
              <h3>Medium-term (3-12 months)</h3>
              <p><strong>Apply for Seed Financing</strong></p>
              <p>Apply to BFPME Innovation Startup Fund</p>
              <p className="text-muted">Effort: Medium | Impact: High</p>
            </div>
          </div>

          <div className="timeline-item">
            <div className="timeline-content">
              <h3>Long-term (12+ months)</h3>
              <p><strong>Prepare for Series A Funding</strong></p>
              <p>Develop growth metrics, build advisory board, prepare pitch deck</p>
              <p className="text-muted">Effort: High | Impact: Very High</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};