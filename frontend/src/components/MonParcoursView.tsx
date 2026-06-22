import React from 'react';

export const MonParcoursView = () => {
  return (
    <div className="card">
      <div className="card-header">
        <h2>Mon Parcours - Your Entrepreneurial Journey</h2>
        <button className="btn btn-secondary">View Full History</button>
      </div>
      <div className="card-content">
        <div className="grid grid-2">
          <div>
            <h3>Journey Progress</h3>
            <div className="progress-bar" style={{ height: '20px' }}>
              <div className="progress-fill" style={{ width: '40%', backgroundColor: '#3498db' }}></div>
            </div>
            <p className="text-muted">40% through Structuration stage</p>
            <p><strong>Current Stage:</strong> Structuration</p>
            <p><strong>Started Journey:</strong> January 15, 2024</p>
            <p><strong>Days in Current Stage:</strong> 45 days</p>
          </div>

          <div>
            <h3>Score Evolution</h3>
            <div style={{ height: '200px' }}>
              {/* In a real app, this would be a chart using recharts or similar */}
              <div className="card" style={{ padding: '1rem', backgroundColor: '#f8f9fa' }}>
                <p className="text-center">Score Trend Visualization</p>
                <p className="text-muted small">(Chart would show Market, Commercial Offer, Innovation, Scalability, Green scores over time)</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card-header" style={{ marginTop: '1.5rem' }}>
          <h3>Recent Activities</h3>
        </div>
        <div style={{ height: '150px', overflowY: 'auto' }}>
          <div className="card" style={{ padding: '0.75rem', marginBottom: '0.5rem', backgroundColor: '#f8f9fa' }}>
            <p><strong>Today</strong> - Completed financial documentation draft</p>
            <p className="text-muted">Action marked as complete</p>
          </div>
          <div className="card" style={{ padding: '0.75rem', marginBottom: '0.5rem', backgroundColor: '#f8f9fa' }}>
            <p><strong>Yesterday</strong> - Updated market validation survey results</p>
            <p className="text-muted">Evidence added to diagnostic profile</p>
          </div>
          <div className="card" style={{ padding: '0.75rem', marginBottom: '0.5rem', backgroundColor: '#f8f9fa' }}>
            <p><strong>2 days ago</strong> - Received scoring update</p>
            <p className="text-muted">Market score improved from 62 to 68</p>
          </div>
        </div>

        <div className="card-header" style={{ marginTop: '1.5rem' }}>
          <h3>Upcoming Milestones</h3>
        </div>
        <ul style={{ paddingLeft: '1.25rem' }}>
          <li><strong>Next Week:</strong> Submit business registration documents to ANPE</li>
          <li><strong>In 2 Weeks:</strong> Complete financial documentation package</li>
          <li><strong>In 1 Month:</strong> Apply for first round of feedback from BFPME mentor</li>
          <li><strong>In 3 Months:</strong> Eligible to apply for seed financing</li>
        </ul>
      </div>
    </div>
  );
};