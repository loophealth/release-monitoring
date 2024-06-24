import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams, Link } from 'react-router-dom';

function ReleaseDetails() {
    const { id } = useParams();
    const [release, setRelease] = useState(null);
    const [actions, setActions] = useState([]);

    useEffect(() => {
        const fetchReleaseDetails = async () => {
            try {
                const response = await axios.get(`http://localhost:8000/releases/${id}`);
                setRelease(response.data);
            } catch (error) {
                console.error('Error fetching release details', error);
            }
        };

        const fetchReleaseActions = async () => {
            try {
                const response = await axios.get(`http://localhost:8000/releases/${id}/actions`);
                setActions(response.data);
            } catch (error) {
                console.error('Error fetching release actions', error);
            }
        };

        fetchReleaseDetails();
        fetchReleaseActions();
    }, [id]);

    return (
        <div>
            {release && (
                <>
                    <h2>Release Details</h2>
                    <p>ID: {release.id}</p>
                    <p>Name: {release.name}</p>
                    <p>State: {release.state}</p>
                    <h3>Actions</h3>
                    <ul>
                        {actions.map((action) => (
                            <li key={action.id}>
                                <p>Environment: {action.env}</p>
                                <p>Version: {action.version}</p>
                                <p>Status: {action.deployment_status}</p>
                                <p>Comment: {action.comment}</p>
                                <p>
                                    Action URL: <a href={action.action_url}>{action.action_url}</a>
                                </p>
                                <p>
                                    Tag URL: <a href={action.tag_url}>{action.tag_url}</a>
                                </p>
                            </li>
                        ))}
                    </ul>
                    <Link to={`/hotfix/${release.id}`}>Apply Hotfix</Link>
                </>
            )}
        </div>
    );
}

export default ReleaseDetails;
