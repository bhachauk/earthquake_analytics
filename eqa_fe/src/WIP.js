import React from 'react';

function WorkInProgress() {
    return (
        <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '100vh', // Optional: Makes it fill the viewport height
            flexDirection: 'column', // Optional: Stack the text and icon
            textAlign: 'center',
        }}>
            <span role="img" aria-label="construction" style={{ fontSize: '3rem' }}>🚧</span>
            <h1>Work in Progress</h1>
            <p>This feature is currently under development. Please check back later.</p>
        </div>
    );
}

export default WorkInProgress;