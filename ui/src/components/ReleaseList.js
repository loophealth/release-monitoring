import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { Card, CardContent, Typography, CardActionArea, Grid, Button, Container } from '@mui/material';

const stateMap = {
    1: 'Testing',
    2: 'Ready for Testing',
    3: 'Tested',
    4: 'Blocked',
    5: 'Ready for Release',
    6: 'Released',
    7: 'Stable'
};

function ReleaseList() {
    const [releases, setReleases] = useState([]);

    useEffect(() => {
        const fetchReleases = async () => {
            try {
                const response = await axios.get('http://localhost:8000/releases/');
                setReleases(response.data);
            } catch (error) {
                console.error('Error fetching releases', error);
            }
        };

        fetchReleases();
    }, []);

    return (
        <Container>
            <Typography variant="h2" component="h1" gutterBottom>
                Releases
            </Typography>
            <Button variant="contained" color="primary" component={Link} to="/create" style={{ marginBottom: '20px' }}>
                Create New Release
            </Button>
            <Grid container spacing={4}>
                {releases.map((release) => (
                    <Grid item xs={12} key={release.id}>
                        <Card>
                            <CardActionArea component={Link} to={`/releases/${release.id}`}>
                                <CardContent>
                                    <Typography variant="h5" component="h2">
                                        {release.name}
                                    </Typography>
                                    <Typography variant="body2" color="textSecondary">
                                        State: {stateMap[release.state]}
                                    </Typography>
                                </CardContent>
                            </CardActionArea>
                        </Card>
                    </Grid>
                ))}
            </Grid>
        </Container>
    );
}

export default ReleaseList;
