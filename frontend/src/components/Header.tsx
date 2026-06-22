import React from 'react';
import { useAuth } from '../context/AuthContext';

interface HeaderProps {
  user?: any; // We'll type this properly once we have the user model
}

export const Header = ({ user }: HeaderProps) => {
  const { logout } = useAuth();

  return (
    <header className="header">
      <div>
        <h1>Entrepreneurial Orientation Engine</h1>
      </div>
      <div className="header-actions">
        <button className="btn btn-secondary" onClick={() => console.log('Notifications clicked')}>
          🔔 Notifications
        </button>
        <button className="btn btn-secondary" onClick={() => console.log('Profile clicked')}>
          👤 Profile
        </button>
        <button className="btn btn-secondary" onClick={logout}>
          🚪 Logout
        </button>
      </div>
    </header>
  );
};