import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './Header';
import Footer from './Footer';
import Home from './Home';
import Area from './Area';
import './App.css';

import '@fortawesome/fontawesome-free/css/all.min.css';

function App() {
    return (
        <Router basename="/earthquake_analytics">
            <div className="app-container">
                <Header />
                <main className="main-content">
                    <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path="/Area" element={<Area />} />
                        {/* Add more routes for your pages */}
                    </Routes>
                </main>
                <Footer />
            </div>
        </Router>
    );
}

export default App;