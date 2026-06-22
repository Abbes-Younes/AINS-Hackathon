import React from 'react';

export const DiagnosticPanel = () => {
  return (
    <div className="card">
      <div className="card-header">
        <h2>Diagnostic Summary</h2>
        <button className="btn btn-secondary">View Details</button>
      </div>
      <div className="card-content">
        <div className="grid grid-2">
          <div>
            <h3>Current Stage</h3>
            <p className="status-badge status-active">Structuration</p>
            <p className="text-muted">Based on evidence trace and self-assessment</p>
          </div>
          <div>
            <h3>Perception Gap</h3>
            <p className="status-badge status-warning">Over-estimation</p>
            <p className="text-muted">You perceive yourself at Fundraising stage, but evidence places you at Structuration</p>
          </div>
        </div>

        <h3>Evidence Trace</h3>
        <div className="card" style={{ padding: '1rem', backgroundColor: '#f8f9fa' }}>
          <p><strong>•</strong> Completed market validation survey (15 responses)</p>
          <p><strong>•</strong> Defined core value proposition</p>
          <p><strong>•</strong> Initial customer interviews conducted (5)</p>
          <p><strong>•</strong> Basic financial projections created</p>
          <p><em>Last updated: Today, 10:30 AM</em></p>
        </div>

        <div className="card-header" style={{ marginTop: '1.5rem' }}>
          <h3>Key Insights</h3>
        </div>
        <ul style={{ paddingLeft: '1.25rem' }}>
          <li>Strong market validation evidence</li>
          <li>Clear value proposition defined</li>
          <li>Area for improvement: financial modeling depth</li>
          <li>Ready for structural formalization</li>
        </ul>
      </div>
    </div>
  );
};