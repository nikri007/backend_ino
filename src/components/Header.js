import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { isAuthenticated, logout } from '../utils/auth';

const Header = () => {
  const navigate = useNavigate();
  
  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  
  return (
    <header className="header">
      <div className="container header-content">
        <h1 className="logo">
          <Link to="/">Contact Manager</Link>
        </h1>
        <nav>
          {isAuthenticated() ? (
            <ul className="nav-links">
              <li>
                <Link to="/"><i className="fas fa-home"></i> Dashboard</Link>
              </li>
              <li>
                <Link to="/add-contact"><i className="fas fa-plus"></i> Add Contact</Link>
              </li>
              <li>
                <button className="btn-link" onClick={handleLogout}>
                  <i className="fas fa-sign-out-alt"></i> Logout
                </button>
              </li>
            </ul>
          ) : (
            <ul className="nav-links">
              <li>
                <Link to="/login"><i className="fas fa-sign-in-alt"></i> Login</Link>
              </li>
              <li>
                <Link to="/register"><i className="fas fa-user-plus"></i> Register</Link>
              </li>
            </ul>
          )}
        </nav>
      </div>
    </header>
  );
};

export default Header;