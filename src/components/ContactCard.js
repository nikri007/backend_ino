import React from 'react';
import { Link } from 'react-router-dom';

const ContactCard = (props) => {
  const { contact, onDelete } = props;
  
  // Parse phone numbers if needed
  const phoneNumbers = typeof contact.phone_numbers === 'string' 
    ? JSON.parse(contact.phone_numbers) 
    : contact.phone_numbers || [];
  
  return (
    <div className="contact-card">
      <div className="contact-header">
        <h3>{contact.first_name} {contact.last_name}</h3>
      </div>
      <div className="contact-body">
        {contact.company && (
          <p className="contact-info">
            <i className="fas fa-building"></i> {contact.company}
          </p>
        )}
        {phoneNumbers.length > 0 && (
          <p className="contact-info">
            <i className="fas fa-phone"></i> {phoneNumbers[0]}
          </p>
        )}
        {contact.address && (
          <p className="contact-info">
            <i className="fas fa-map-marker-alt"></i> {contact.address}
          </p>
        )}
        <div className="contact-actions">
          <Link to={`/contacts/${contact.id}`} className="btn btn-primary">
            <i className="fas fa-eye"></i> View
          </Link>
          <Link to={`/edit-contact/${contact.id}`} className="btn btn-secondary">
            <i className="fas fa-edit"></i> Edit
          </Link>
          <button onClick={() => onDelete(contact.id)} className="btn btn-danger">
            <i className="fas fa-trash"></i> Delete
          </button>
        </div>
      </div>
    </div>
  );
};

export default ContactCard;