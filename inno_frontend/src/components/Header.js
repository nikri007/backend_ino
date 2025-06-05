import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { isAuthenticated, logout, getUserData } from '../utils/auth';

const Header = () => {
  const navigate = useNavigate();
  const userData = getUserData();
  
  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  
  // Get profile picture URL
  const getProfilePictureUrl = () => {
    if (userData && userData.profile_picture) {
      return `http://localhost:5000/uploads/${userData.profile_picture}`;
    }
    return null;
  };

  // Get user's initials for fallback
  const getUserInitials = () => {
    if (userData && userData.first_name && userData.last_name) {
      return `${userData.first_name.charAt(0)}${userData.last_name.charAt(0)}`.toUpperCase();
    }
    return 'U';
  };

  // Get user's full name
  const getUserName = () => {
    if (userData && userData.first_name && userData.last_name) {
      return `${userData.first_name} ${userData.last_name}`;
    }
    return 'User';
  };

  const profilePictureUrl = getProfilePictureUrl();
  
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
              
              {/* User Profile Section */}
              <li className="user-profile">
                <div className="profile-info">
                  <div className="profile-picture-container">
                    {profilePictureUrl ? (
                      <>
                        <img 
                          src={profilePictureUrl} 
                          alt="Profile" 
                          className="profile-picture-small"
                          onError={(e) => {
                            e.target.style.display = 'none';
                            e.target.nextSibling.style.display = 'flex';
                          }}
                        />
                        <div 
                          className="profile-initials" 
                          style={{ display: 'none' }}
                        >
                          {getUserInitials()}
                        </div>
                      </>
                    ) : (
                      <div 
                        className="profile-initials" 
                        style={{ display: 'flex' }}
                      >
                        {getUserInitials()}
                      </div>
                    )}
                  </div>
                  <span className="user-name">{getUserName()}</span>
                </div>
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