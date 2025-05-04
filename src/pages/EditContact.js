import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { toast } from 'react-toastify';
import { contactService } from '../services/api';

const EditContact = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    address: '',
    company: '',
    phone_numbers: ['']
  });
  const [loading, setLoading] = useState(false);
  const [fetchLoading, setFetchLoading] = useState(true);
  
  useEffect(() => {
    const fetchContact = async () => {
      try {
        const response = await contactService.getById(id);
        const contact = response.data;
        
        // Parse phone numbers if they're stored as a string
        const phoneNumbers = typeof contact.phone_numbers === 'string' 
          ? JSON.parse(contact.phone_numbers) 
          : contact.phone_numbers || [''];
        
        setFormData({
          first_name: contact.first_name,
          last_name: contact.last_name,
          address: contact.address || '',
          company: contact.company || '',
          phone_numbers: phoneNumbers.length > 0 ? phoneNumbers : ['']
        });
      } catch (err) {
        toast.error('Failed to fetch contact details');
        navigate('/');
      } finally {
        setFetchLoading(false);
      }
    };
    
    fetchContact();
  }, [id, navigate]);
  
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
      await contactService.update(id, formData);
      toast.success('Contact updated successfully!');
      navigate('/');
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to update contact');
    } finally {
      setLoading(false);
    }
  };
  
  if (fetchLoading) {
    return <div className="loading">Loading contact details...</div>;
  }
  
  return (
    <div className="form-container">
      <div className="form-card">
        <h2>Edit Contact</h2>
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
              {loading ? 'Updating...' : 'Update Contact'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EditContact;