import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import { authService } from '../services/api';
import { saveUserData } from '../utils/auth';

const Register = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    confirm_password: '',
    date_of_birth: '',
    gender: '',
    phone_numbers: [''],
    address: '',
    profile_picture: null
  });
  const [loading, setLoading] = useState(false);
  const [imagePreview, setImagePreview] = useState(null);
  
  const handleChange = e => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };
  
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setFormData({ ...formData, profile_picture: file });
    
    // Create image preview
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => setImagePreview(e.target.result);
      reader.readAsDataURL(file);
    } else {
      setImagePreview(null);
    }
  };
  
  // Handle DD/MM/YYYY date input with auto-formatting
  const handleDateChange = (e) => {
    let value = e.target.value;
    
    // Remove any non-digit characters
    value = value.replace(/\D/g, '');
    
    // Auto-format as DD/MM/YYYY
    if (value.length >= 2) {
      value = value.substring(0, 2) + '/' + value.substring(2);
    }
    if (value.length >= 5) {
      value = value.substring(0, 5) + '/' + value.substring(5);
    }
    
    // Limit to 10 characters (DD/MM/YYYY)
    value = value.substring(0, 10);
    
    setFormData({ ...formData, date_of_birth: value });
  };
  
  // Convert DD/MM/YYYY to YYYY-MM-DD for backend
  const convertDateForBackend = (dateStr) => {
    if (!dateStr || dateStr.length !== 10) return '';
    
    const [day, month, year] = dateStr.split('/');
    
    // Validate date components
    if (!day || !month || !year || day.length !== 2 || month.length !== 2 || year.length !== 4) {
      return '';
    }
    
    // Basic validation
    const dayNum = parseInt(day);
    const monthNum = parseInt(month);
    const yearNum = parseInt(year);
    
    if (dayNum < 1 || dayNum > 31 || monthNum < 1 || monthNum > 12 || yearNum < 1900 || yearNum > 2010) {
      return '';
    }
    
    return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
  };
  
  const handlePhoneChange = (index, value) => {
    const updatedPhones = [...formData.phone_numbers];
    updatedPhones[index] = value;
    setFormData({ ...formData, phone_numbers: updatedPhones });
  };
  
  const addPhoneField = () => {
    setFormData({
      ...formData,
      phone_numbers: [...formData.phone_numbers, '']
    });
  };
  
  const removePhoneField = index => {
    const updatedPhones = formData.phone_numbers.filter((_, i) => i !== index);
    setFormData({ ...formData, phone_numbers: updatedPhones });
  };
  
  const removeImage = () => {
    setFormData({ ...formData, profile_picture: null });
    setImagePreview(null);
    // Reset file input
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) fileInput.value = '';
  };
  
  const validateDate = (dateStr) => {
    if (!dateStr || dateStr.length !== 10) {
      return false;
    }
    
    const [day, month, year] = dateStr.split('/');
    const date = new Date(year, month - 1, day);
    
    return date.getDate() == day && 
           date.getMonth() == month - 1 && 
           date.getFullYear() == year &&
           date.getFullYear() >= 1900 &&
           date.getFullYear() <= 2010;
  };
  
  const handleSubmit = async e => {
    e.preventDefault();
    
    if (formData.password !== formData.confirm_password) {
      toast.error('Passwords do not match');
      return;
    }
    
    // Validate date
    if (!validateDate(formData.date_of_birth)) {
      toast.error('Please enter a valid date of birth in DD/MM/YYYY format');
      return;
    }
    
    setLoading(true);
    
    try {
      // Create FormData for file upload support
      const submitData = new FormData();
      
      // Add all text fields to FormData
      submitData.append('first_name', formData.first_name);
      submitData.append('last_name', formData.last_name);
      submitData.append('email', formData.email);
      submitData.append('password', formData.password);
      submitData.append('confirm_password', formData.confirm_password);
      
      // Convert date to backend format (YYYY-MM-DD)
      const backendDate = convertDateForBackend(formData.date_of_birth);
      submitData.append('date_of_birth', backendDate);
      
      submitData.append('gender', formData.gender);
      submitData.append('address', formData.address);
      
      // Filter out empty phone numbers and stringify
      const validPhones = formData.phone_numbers.filter(phone => phone.trim() !== '');
      submitData.append('phone_numbers', JSON.stringify(validPhones));
      
      // Add profile picture if selected
      if (formData.profile_picture) {
        submitData.append('profile_picture', formData.profile_picture);
        console.log('Profile picture attached:', formData.profile_picture.name);
      }
      
      // Debug: Log all FormData entries
      for (let [key, value] of submitData.entries()) {
        console.log(`FormData ${key}:`, value);
      }
      
      console.log('Submitting registration with profile picture:', formData.profile_picture ? 'Yes' : 'No');
      
      const response = await authService.register(submitData);
      saveUserData(response.data.token, response.data.user);
      toast.success('Registration successful!');
      navigate('/');
    } catch (err) {
      console.error('Registration error:', err);
      const errorMessage = err.response?.data?.error;
      if (typeof errorMessage === 'object') {
        // Handle validation errors
        const errors = Object.values(errorMessage).flat();
        toast.error(`Registration failed: ${errors.join(', ')}`);
      } else {
        toast.error(errorMessage || 'Registration failed');
      }
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Create an Account</h2>
        <form onSubmit={handleSubmit}>
          
          {/* Profile Picture Section */}
          <div className="form-group">
            <label>Profile Picture (Optional)</label>
            <div className="profile-picture-section">
              <input
                type="file"
                accept="image/png,image/jpg,image/jpeg,image/gif"
                onChange={handleFileChange}
                className="file-input"
              />
              <small className="file-help">Choose JPG, PNG, or GIF. Max size: 16MB</small>
              
              {imagePreview && (
                <div className="image-preview">
                  <img src={imagePreview} alt="Profile Preview" />
                  <button 
                    type="button" 
                    className="remove-image-btn"
                    onClick={removeImage}
                    title="Remove image"
                  >
                    <i className="fas fa-times"></i>
                  </button>
                </div>
              )}
            </div>
          </div>
          
          <div className="form-row">
            <div className="form-group">
              <label>First Name</label>
              <input
                type="text"
                name="first_name"
                value={formData.first_name}
                onChange={handleChange}
                placeholder="Enter first name"
                required
              />
            </div>
            <div className="form-group">
              <label>Last Name</label>
              <input
                type="text"
                name="last_name"
                value={formData.last_name}
                onChange={handleChange}
                placeholder="Enter last name"
                required
              />
            </div>
          </div>
          
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="Enter email address"
              required
            />
          </div>
          
          <div className="form-row">
            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Enter password"
                required
              />
            </div>
            <div className="form-group">
              <label>Confirm Password</label>
              <input
                type="password"
                name="confirm_password"
                value={formData.confirm_password}
                onChange={handleChange}
                placeholder="Confirm password"
                required
              />
            </div>
          </div>
          
          <div className="form-row">
            <div className="form-group">
              <label>Date of Birth</label>
              <input
                type="text"
                name="date_of_birth"
                value={formData.date_of_birth}
                onChange={handleDateChange}
                placeholder="DD/MM/YYYY"
                maxLength="10"
                required
              />
              <small className="date-help">
                {formData.date_of_birth 
                  ? (validateDate(formData.date_of_birth) 
                      ? `✓ Valid date: ${formData.date_of_birth}` 
                      : '✗ Invalid date format')
                  : 'Enter date in DD/MM/YYYY format'
                }
              </small>
            </div>
            <div className="form-group">
              <label>Gender</label>
              <select
                name="gender"
                value={formData.gender}
                onChange={handleChange}
                required
              >
                <option value="">Select Gender</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>
          
          <div className="form-group">
            <label>Address</label>
            <textarea
              name="address"
              value={formData.address}
              onChange={handleChange}
              placeholder="Enter your address"
              required
            ></textarea>
          </div>
          
          <div className="form-group">
            <label>Phone Numbers</label>
            {formData.phone_numbers.map((phone, index) => (
              <div key={index} className="phone-input">
                <input
                  type="tel"
                  value={phone}
                  onChange={e => handlePhoneChange(index, e.target.value)}
                  placeholder="Enter phone number"
                />
                {index > 0 && (
                  <button 
                    type="button" 
                    className="btn-icon" 
                    onClick={() => removePhoneField(index)}
                  >
                    <i className="fas fa-times"></i>
                  </button>
                )}
              </div>
            ))}
            <button 
              type="button" 
              className="btn btn-secondary btn-sm" 
              onClick={addPhoneField}
            >
              <i className="fas fa-plus"></i> Add Phone Number
            </button>
          </div>
          
          <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
            {loading ? 'Registering...' : 'Register'}
          </button>
        </form>
        <p className="auth-link">
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  );
};

export default Register;