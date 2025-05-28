import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Import Font Awesome
import '@fortawesome/fontawesome-free/css/all.min.css';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import ContactDetails from './pages/ContactDetails';
import AddContact from './pages/AddContact';
import EditContact from './pages/EditContact';

// Components
import Header from './components/Header';

// Utils
import { isAuthenticated } from './utils/auth';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  if (!isAuthenticated()) {
    return <Navigate to="/login" />;
  }
  return children;
};

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <div className="container">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
            <Route path="/contacts/:id" element={
              <ProtectedRoute>
                <ContactDetails />
              </ProtectedRoute>
            } />
            <Route path="/add-contact" element={
              <ProtectedRoute>
                <AddContact />
              </ProtectedRoute>
            } />
            <Route path="/edit-contact/:id" element={
              <ProtectedRoute>
                <EditContact />
              </ProtectedRoute>
            } />
          </Routes>
        </div>
        <ToastContainer position="bottom-right" />
      </div>
    </Router>
  );
}

export default App;
