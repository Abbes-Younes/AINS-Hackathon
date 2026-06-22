import React from 'react';

export const Roadmap = () => {
  return (
    <div className="app">
      <div className="main-content">
        <div className="container">
          <h1>Personalized Roadmap</h1>
          <p className="text-muted">Your sequenced action plan based on diagnostic and scoring results</p>

          <div className="card">
            <div className="card-header">
              <h2>Roadmap Overview</h2>
              <p className="text-muted">Actions sequenced by time horizon and dependency</p>
            </div>
            <div className="card-content">
              <div className="tabs">
                <button className="tab-btn active" data-tab="immediate">Immediate (0-30 days)</button>
                <button className="tab-btn" data-tab="short-term">Short-term (1-3 months)</button>
                <button className="tab-btn" data-tab="medium-term">Medium-term (3-12 months)</button>
                <button className="tab-btn" data-tab="long-term">Long-term (12+ months)</button>
              </div>

              <div className="tab-content active" id="immediate-tab">
                <div className="card" style={{ padding: '1rem', backgroundColor: '#fff3cd', border: '1px solid #ffeaa7' }}>
                  <h3 style={{ color: '#856404', marginTop: 0 }}>Priority: HIGH</h3>
                  <div className="roadmap-item">
                    <h4>Complete Financial Documentation Package</h4>
                    <p>Use the BFPME pre-financing template to create detailed 3-year financial projections including income statement, balance sheet, and cash flow statements.</p>
                    <div className="roadmap-meta">
                      <span>Effort: High</span>
                      <span>Impact: High</span>
                      <span>Prerequisites: None</span>
                    </div>
                    <div className="roadmap-resources">
                      <strong>Linked Resources:</strong>
                      <ul style={{ marginLeft: '1.25rem', marginTop: '0.5rem' }}>
                        <li><a href="#" target="_blank" rel="noopener noreferrer">BFPME Pre-Financing Guide</a></li>
                        <li><a href="#" target="_blank" rel="noopener noreferrer">Financial Modeling Template (Excel)</a></li>
                        <li><a href="#" target="_blank" rel="noopener noreferrer">Unit Economics Worksheet</a></li>
                      </ul>
                    </div>
                  </div>
                </div>

                <div className="card" style={{ padding: '1rem', backgroundColor: '#fff3cd', border: '1px solid #ffeaa7', marginTop: '1rem' }}>
                  <h3 style={{ color: '#856404', marginTop: 0 }}>Priority: HIGH</h3>
                  <div className="roadmap-item">
                    <h4>Initial Market Validation Survey</h4>
                    <p>Design and execute a structured customer validation survey with at least 30 potential customers to validate demand and pricing sensitivity.</p>
                    <div className="roadmap-meta">
                      <span>Effort: Medium</span>
                      <span>Impact: High</span>
                      <span>Prerequisites: None</span>
                    </div>
                    <div className="roadmap-resources">
                      <strong>Linked Resources:</strong>
                      <ul style={{ marginLeft: '1.25rem', marginTop: '0.5rem' }}>
                        <li><a href="#" target="_blank" rel="noopener noreferrer">Customer Survey Template</a></li>
                        <li><a href="#" target="_blank" rel="noopener noreferrer">Interview Guide Template</a></li>
                        <li><a href="#" target="_blank" rel="noopener noreferrer">Survey Incentive Guidelines</a></li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>

              <div className="tab-content" id="short-term-tab">
                <div className="card" style={{ padding: '1rem', backgroundColor: '#d1ecf1', border: '1px solid #bee5eb' }}>
                  <h3 style={{ color: '#0c5460', marginTop: 0 }}>Priority: MEDIUM</h3>
                  <div className="roadmap-item">
                    <h4>Formal Legal Registration</h4>
                    <p>Register your business as a SARL (Société À Responsabilité Limitée) through the ANPE online portal, including obtaining tax ID, commerce registration, and publication in the official gazette.</p>
                    <div className="roadmap-meta">
                      <span>Effort: Medium</span>
                      <span>Impact: High</span>
                      <span>Prerequisites: Completed financial documentation</span>
                    </div>
                    <div className="roadmap-resources">
                      <strong>Linked Resources:</strong>
                      <ul style={{ marginLeft: '1.25rem', marginTop: '0.5rem' }}>
                        <li><a href="#" target="_blank" rel="noopener noreferrer">ANPE Business Registration Guide</a></li>
                        <li><a href="#" target="_blank" rel="noopener noreferrer">Legal Form Comparison Guide</a></li>
                        <li><a href="#" target="_blank" rel="noopener noreferrer">Registration Fee Schedule</a></li>
                      </ul>
                    </div>
                  </div>
                </div>

                <div className="card" style={{ padding: '1rem', backgroundColor: '#d1ecf1', border: '1px solid #bee5eb', marginTop: '1rem' }}>
                  <h3 style={{ color: '#0c5460', marginTop: 0 }}>Priority: MEDIUM</h3>
                  <div className="roadmap-item">
                    <h4>Minimum Viable Product (MVP) Development</h4>
                    <p>Develop a functional MVP based on validated customer feedback, focusing on core features that address the primary value proposition.</p>
                    <div className="roadmap-meta">
                      <span>Effort: High</span>
                      <span>Impact: Medium</span>
                      <span>Prerequisites: Market validation completed</span>
                    </div>
                    <div className="roadmap-resources">
                      <strong>Linked Resources:</strong>
                      <ul style={{ marginLeft: '1.25rem', marginTop: '0.5rem' }}>
                        <li><a href="#" target="_blank" rel="noopener noreferrer">MVP Development Framework</a></li>
                        <li><a href="#" target="_blank" rel="noopener noreferrer">Agile Methodology Guide</a></li>
                        <li><a href="#" target="_blank" rel="noopener noreferrer">Protoboarding Tools List</a></li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>

              <div className="tab-content" id="medium-term-tab">
                <div className="card" style={{ padding: '1rem', backgroundColor: '#e8f4fc', border: '1px solid #bee5eb' }}>
                  <h3 style={{ color: '#0c5460', marginTop: 0 }}>Priority: MEDIUM</h3>
                  <div className="roadmap-item">
                    <h4>Apply for Seed Financing</h4>
                    <p>Apply for seed financing through BFPME's Innovation Startup Fund once financial documentation is complete and legal structure is formalized.</p>
                    <div className="roadmap-meta">
                      <span>Effort: High</span>
                      <span>Impact: Very High</span>
                      <span>Prerequisites: Financial documentation complete + Legal registration completed</span>
                    </div>
                    <div className="roadmap-resources">
                      <strong>Linked Resources:</strong>
                      <ul style={{ marginLeft: '1.25rem', marginTop: '0.5rem' }}>
                        <li><a href="#" target="_blank" rel="noopener noreferrer">BFPME Innovation Startup Fund Guide</a></li>
                        <li><a href="#" target="_blank" rel="noopener noreferrer">Loan Application Checklist</a></li>
                        <li><a href="#" target="_blank" rel="noopener noreferrer">Investor Pitch Deck Template</a></li>
                      </ul>
                    </div>
                  </div>
                </div>

                <div className="card" style={{ padding: '1rem', backgroundColor: '#e8f4fc', border: '1px solid #bee5eb', marginTop: '1rem' }}>
                  <h3 style={{ color: '#0c5460', marginTop: 0 }}>Priority: MEDIUM</h3>
                  <div className="roadmap-item">
                    <h4>Strategic Partnership Development</h4>
                    <p>Identify and establish 2-3 strategic partnerships with complementary businesses or industry associations to expand market reach and capabilities.</p>
                    <div className="roadmap-meta">
                      <span>Effort: Medium</span>
                      <span>Impact: Medium</span>
                      <span>Prerequisites: MVP developed + Initial customer feedback</span>
                    </div>
                    <div className="roadmap-resources">
                      <strong>Linked Resources:</strong>
                      <ul style={{ marginLeft: '1.25rem', marginTop: '0.5rem' }}>
                        <li><a href="#" target="_blank" rel="noopener noreferrer">Partnership Proposal Template</a></li>
                        <li><a href="#" target="_blank" rel="noopener noreferrer">Networking Events Calendar</a></li>
                        <li><a href="#" target="_blank" rel="noopener noreffer">MOU Template</a></li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>

              <div className="tab-content" id="long-term-tab">
                <div className="card" style={{ padding: '1rem', backgroundColor: '#fcebd9', border: '1px solid #fdcb6e' }}>
                  <h3 style={{ color: '#636e72', marginTop: 0 }}>Priority: LOW-MEDIUM</h3>
                  <div className="roadmap-item">
                    <h4>Prepare for Series A Funding</h4>
                    <p>Develop growth metrics, build advisory board, refine pitch deck, and establish relationships with potential institutional investors for Series A round.</p>
                    <div className="roadmap-meta">
                      <span>Effort: Very High</span>
                      <span>Impact: Very High</span>
                      <span>Prerequisites: Seed financing secured + Demonstrated traction + Scalable operations</span>
                    </div>
                    <div className="roadmap-resources">
                      <strong>Linked Resources:</strong>
                      <ul style={{ marginLeft: '1.25rem', marginTop: '0.5rem' }}>
                        <li><a href="#" target="_blank" rel="noopener noreferrer">Series A Preparation Guide</a></li>
                        <li><a href="#" target="_blank" rel="noopener noreferrer">Investor Relations Best Practices</a></li>
                        <li><a href="#" target="_blank" rel="noopener noreferrer">Term Sheet Negotiation Guide</a></li>
                      </ul>
                    </div>
                  </div>
                </div>

                <div className="card" style={{ padding: '1rem', backgroundColor: '#fcebd9', border: '1px solid #fdcb6e', marginTop: '1rem' }}>
                  <h3 style={{ color: '#636e72', marginTop: 0 }}>Priority: LOW-MEDIUM</h3>
                  <div className="roadmap-item">
                    <h4>Market Expansion Planning</h4>
                    <p>Develop strategy for expanding beyond initial market, potentially to other Tunisian cities or regional markets.</p>
                    <div className="roadmap-meta">
                      <span>Effort: High</span>
                      <span>Impact: Medium</span>
                      <span>Prerequisites: Product-market fit achieved + Operational processes stabilized</span>
                    </div>
                    <div className="roadmap-resources">
                      <strong>Linked Resources:</strong>
                      <ul style={{ marginLeft: '1.25rem', marginTop: '0.5rem' }}>
                        <li><a href="#" target="_blank" rel="noopener noreferrer">Market Expansion Framework</a></li>
                        <li><a href="#" target="_blank" rel="noopener noreferrer">Regional Business Regulations Guide</a></li>
                        <li><a href="#" target="_blank" rel="noopener noreferrer">Logistics and Supply Chain Guide</a></li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};