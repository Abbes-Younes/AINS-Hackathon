import React from 'react';

export const PriorityBlockers = () => {
  return (
    <div className="card">
      <div className="card-header">
        <h2>Priority Blockers</h2>
        <button className="btn btn-secondary">View All</button>
      </div>
      <div className="card-content">
        <div className="card" style={{ padding: '1rem', backgroundColor: '#fff3cd', border: '1px solid #ffeaa7' }}>
          <h3 style={{ color: '#856404', marginTop: 0 }}>High Priority</h3>
          <p style={{ marginBottom: '0.5rem' }}><strong>Financial Documentation</strong></p>
          <p style={{ margin: 0, fontSize: '0.9rem' }}>Missing detailed financial projections and unit economics preventing financing applications</p>
        </div>

        <div className="card" style={{ padding: '1rem', backgroundColor: '#f8d7da', border: '1px solid #f5c6cb' }} style={{ marginTop: '1rem' }}>
          <h3 style={{ color: '#721c24', marginTop: 0 }}>Medium Priority</h3>
          <p style={{ marginBottom: '0.5rem' }}><strong>Legal Structure</strong></p>
          <p style={{ margin: 0, fontSize: '0.9rem' }}>Business not yet registered as formal legal entity (SARL/SA)</p>
        </div>

        <div className="card" style={{ padding: '1rem', backgroundColor: '#d1ecf1', border: '1px solid #bee5eb' }} style={{ marginTop: '1rem' }}>
          <h3 style={{ color: '#0c5460', marginTop: 0 }}>Low Priority</h3>
          <p style={{ marginBottom: '0.5rem' }}><strong>Team Expansion</strong></p>
          <p style={{ margin: 0, fontSize: '0.9rem' }}>Need to hire marketing specialist to complement technical co-founder</p>
        </div>

        <div className="card-header" style={{ marginTop: '1.5rem' }}>
          <h3>Blocker Impact Analysis</h3>
        </div>
        <p className="text-muted">Resolving the top two blockers would increase your Readiness Score by approximately 22 points and unlock eligibility for 3 additional financing programs.</p>
      </div>
    </div>
  );
};