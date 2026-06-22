import React from 'react';

export const RecommendedActions = () => {
  return (
    <div className="card">
      <div className="card-header">
        <h2>Recommended Actions</h2>
        <button className="btn btn-secondary">View All</button>
      </div>
      <div className="card-content">
        <div className="card" style={{ padding: '1rem', backgroundColor: '#e8f4fc', border: '1px solidsbee' }}>
          <h3 style={{ marginTop: 0 }}>Immediate Action (0-30 days)</h3>
          <p><strong>Complete Financial Documentation Package</strong></p>
          <p>Use the BFPME pre-financing template to create detailed 3-year financial projections, including income statement, balance sheet, and cash flow statements.</p>
          <div className="card-header" style={{ marginTop: '1rem', borderTop: '1px solid #ddd' }}>
            <p><strong>Linked Resource:</strong> <a href="#" target="_blank" rel="noopener noreferrer">BFPME Pre-Financing Guide</a></p>
            <p><strong>Impact:</strong> Resolves financial documentation blocker, enables financing applications</p>
          </div>
        </div>

        <div className="card" style={{ padding: '1rem', backgroundColor: '#e8f4fc', border: '1px solid #bee5eb', marginTop: '1rem' }}>
          <h3 style={{ marginTop: 0 }}>Short-term Action (1-3 months)</h3>
          <p><strong>Formalize Legal Structure</strong></p>
          <p>Register your business as a SARL (Société À Responsabilité Limitée) through the ANPE online portal, including obtaining tax ID and publication in the official gazette.</p>
          <div className="card-header" style={{ marginTop: '1rem', borderTop: '1px solid #ddd' }}>
            <p><strong>Linked Resource:</strong> <a href="#" target="_blank" rel="noopener noreferrer">ANPE Business Registration Guide</a></p>
            <p><strong>Impact:</strong> Resolves legal structure blocker, improves credibility with investors and partners</p>
          </div>
        </div>

        <div className="card" style={{ padding: '1rem', backgroundColor: '#e8f4fc', border: '1px solid #bee5eb', marginTop: '1rem' }}>
          <h3 style={{ marginTop: 0 }}>Medium-term Action (3-12 months)</h3>
          <p><strong>Apply for Seed Financing</strong></p>
          <p>Once financial documentation is complete and legal structure is formalized, apply for seed financing through BFPME's Innovation Startup Fund (up to 100,000 TND).</p>
          <div className="card-header" style={{ marginTop: '1rem', borderTop: '1px solid #ddd' }}>
            <p><strong>Linked Resource:</strong> <a href="#" target="_blank" rel="noopener noreferrer">BFPME Innovation Startup Fund</a></p>
            <p><strong>Prerequisites:</strong> Completed financial documentation + Formal legal structure</p>
          </div>
        </div>
      </div>
    </div>
  );
};