import React, { useState, useEffect } from 'react';
import { DiagnosticPanel } from '../components/DiagnosticPanel';
import { ScoresOverview } from '../components/ScoresOverview';
import { PriorityBlockers } from '../components/PriorityBlockers';
import { RecommendedActions } from '../components/RecommendedActions';
import { RoadmapOverview } from '../components/RoadmapOverview';
import { MonParcoursView } from '../components/MonParcoursView';

export const Dashboard = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Simulate data loading
    setLoading(true);

    // In a real app, this would fetch data from the backend APIs
    // For now, we'll simulate with a timeout
    const timer = setTimeout(() => {
      setLoading(false);
    }, 1500);

    return () => clearTimeout(timer);
  }, []);

  if (loading) {
    return (
      <div className="app">
        <div className="main-content">
          <div className="container">
            <div className="card">
              <h2>Loading Dashboard...</h2>
              <p>Please wait while we load your entrepreneurial profile.</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="app">
        <div className="main-content">
          <div className="container">
            <div className="card">
              <h2>Error Loading Dashboard</h2>
              <p>{error}</p>
              <button className="btn btn-primary" onClick={() => window.location.reload()}>
                Retry
              </button>
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
          <h1>Entrepreneur Dashboard</h1>
          <p className="lead">Your personalized entrepreneurial orientation engine</p>

          <div className="grid grid-2">
            <DiagnosticPanel />
            <ScoresOverview />
          </div>

          <div className="grid grid-2">
            <PriorityBlockers />
            <RecommendedActions />
          </div>

          <RoadmapOverview />

          <MonParcoursView />
        </div>
      </div>
    </div>
  );
};