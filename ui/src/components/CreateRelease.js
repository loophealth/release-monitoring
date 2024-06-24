
import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function CreateRelease() {
  const [name, setName] = useState('');
  const history = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://localhost:8000/releases/', { name });
      history('/');
    } catch (error) {
      console.error('Error creating release', error);
    }
  };

  return (
    <div>
      <h2>Create Release</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Release Name:</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>
        <button type="submit">Create</button>
      </form>
    </div>
  );
}

export default CreateRelease;
