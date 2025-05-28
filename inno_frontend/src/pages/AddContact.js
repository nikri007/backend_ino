import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { contactService } from '../services/api';

const AddContact = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    address: '',
    company: '',
    phone_numbers: ['']
  });
  const [loading, setLoading] = useState(false);
  
  const handleChange = e => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
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
  
  const handleSubmit = async e => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await contactService.create(formData);
      toast.success('Contact added successfully!');
      navigate('/');
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to add contact');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="form-container">
      <div className="form-card">
        <h2>Add New Contact</h2>
        <form onSubmit={handleSubmit}>
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
            <label>Company</label>
            <input
              type="text"
              name="company"
              value={formData.company}
              onChange={handleChange}
              placeholder="Enter company name (optional)"
            />
          </div>
          
          <div className="form-group">
            <label>Address</label>
            <textarea
              name="address"
              value={formData.address}
              onChange={handleChange}
              placeholder="Enter address (optional)"
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
          
          <div className="form-actions">
            <button type="button" className="btn btn-secondary" onClick={() => navigate('/')}>
              <i className="fas fa-arrow-left"></i> Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Adding...' : 'Add Contact'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddContact;