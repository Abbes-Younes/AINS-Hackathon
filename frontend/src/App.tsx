import React from 'react';
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Diagnostic from './pages/Diagnostic';
import Scoring from './pages/Scoring';
import Roadmap from './pages/Roadmap';
import Resources from './pages/Resources';
import Assistant from './pages/Assistant';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { useAuth } from './context/AuthContext';

function App() {
  const { user, isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return (
      <div className="app">
        <div className="main-content">
          <div className="container">
            <h1>Entrepreneurial Orientation Engine</h1>
            <p>Please log in to access the dashboard.</p>
            {/* In a real app, this would redirect to login page */}
          </div>
        </div>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <div className="app">
        <Sidebar />
        <div className="main-content">
          <Header user={user} />
          <div className="container">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/diagnostic" element={<Diagnostic />} />
              <Route path="/scoring" element={<Scoring />} />
              <Route path="/roadmap" element={<Roadmap />} />
              <Route path="/resources" element={<Resources />} />
              <Route path="/assistant" element={<Assistant />} />
              <Route path="*" element={<Dashboard />} />
            </Routes>
          </div>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;