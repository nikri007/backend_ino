import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import { contactService } from '../services/api';

const ContactDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [contact, setContact] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchContactDetails = async () => {
      try {
        const response = await contactService.getById(id);
        setContact(response.data);
      } catch (err) {
        toast.error('Failed to fetch contact details');
        navigate('/');
      } finally {
        setLoading(false);
      }
    };
    
    fetchContactDetails();
  }, [id, navigate]);
  
  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this contact?')) {
      try {
        await contactService.delete(id);
        toast.success('Contact deleted successfully');
        navigate('/');
      } catch (err) {
        toast.error('Failed to delete contact');
      }
    }
  };
  
  if (loading) {
    return <div className="loading">Loading contact details...</div>;
  }
  
  if (!contact) {
    return <div className="alert alert-danger">Contact not found</div>;
  }
  
  // Parse phone numbers if needed
  const phoneNumbers = typeof contact.phone_numbers === 'string' 
    ? JSON.parse(contact.phone_numbers) 
    : contact.phone_numbers || [];
  
  return (
    <div className="form-container">
      <div className="form-card">
        <h2>{contact.first_name} {contact.last_name}</h2>
        
        <div className="contact-details">
          {contact.company && (
            <div className="detail-item">
              <span className="detail-label"><i className="fas fa-building"></i> Company:</span>
              <span className="detail-value">{contact.company}</span>
            </div>
          )}
          
          {contact.address && (
            <div className="detail-item">
              <span className="detail-label"><i className="fas fa-map-marker-alt"></i> Address:</span>
              <span className="detail-value">{contact.address}</span>
            </div>
          )}
          
          {phoneNumbers.length > 0 && (
            <div className="detail-item">
              <span className="detail-label"><i className="fas fa-phone"></i> Phone Numbers:</span>
              <div className="detail-value">
                {phoneNumbers.map((phone, index) => (
                  <div key={index}>{phone}</div>
                ))}
              </div>
            </div>
          )}
          
          <div className="detail-item">
            <span className="detail-label"><i className="fas fa-calendar-alt"></i> Added on:</span>
            <span className="detail-value">
              {new Date(contact.created_at).toLocaleDateString()}
            </span>
          </div>
        </div>
        
        <div className="form-actions">
          <button className="btn btn-secondary" onClick={() => navigate('/')}>
            <i className="fas fa-arrow-left"></i> Back
          </button>
          <div>
            <Link to={`/edit-contact/${contact.id}`} className="btn btn-primary">
              <i className="fas fa-edit"></i> Edit
            </Link>
            <button className="btn btn-danger" onClick={handleDelete} style={{ marginLeft: '10px' }}>
              <i className="fas fa-trash"></i> Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContactDetails;