import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate, useParams } from 'react-router-dom';

function HotfixRelease() {
    const { id } = useParams();
    const [commits, setCommits] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const commitsArray = commits.split(',').map((commit) => commit.trim());
            await axios.post(`http://localhost:8000/releases/${id}/hotfix`, { release_id: id, commits: commitsArray });
            navigate(`/releases/${id}`);
        } catch (error) {
            console.error('Error applying hotfix', error);
        }
    };

    return (
        <div>
            <h2>Apply Hotfix</h2>
            <form onSubmit={handleSubmit}>
                <div>
                    <label>Commits (comma separated):</label>
                    <input type="text" value={commits} onChange={(e) => setCommits(e.target.value)} required />
                </div>
                <button type="submit">Apply Hotfix</button>
            </form>
        </div>
    );
}

export default HotfixRelease;
