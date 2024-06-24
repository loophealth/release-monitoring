import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import CreateRelease from './components/CreateRelease';
import ReleaseList from './components/ReleaseList';
import ReleaseDetails from './components/ReleaseDetails';
import HotfixRelease from './components/HotfixRelease';

function App() {
    return (
        <Router>
            <div className="container">
                <h1>Release Manager</h1>
                <Routes>
                    <Route path="/" exact element={<ReleaseList />} />
                    <Route path="/create" element={<CreateRelease />} />
                    <Route path="/releases/:id" element={<ReleaseDetails />} />
                    <Route path="/hotfix/:id" element={<HotfixRelease />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
