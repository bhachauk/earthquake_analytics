import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Header.css';
import appIcon from './Assets/white_beard_icon.png';

function Header() {
    const location = useLocation();

    return (
        <header className="fixed-header">
            <img src={appIcon} alt="Application Icon" className="app-icon"/>
            <h1 className="header-title">Earthquake Analytics</h1>
            <div className="navigation-bar">
                <nav className="header-nav">
                    <Link to="/" className={location.pathname === '/' ? 'active' : ''}>
                        Home
                    </Link>
                    <Link
                        to="/area"
                        className={location.pathname === '/area' ? 'active' : ''}
                    >
                        Area
                    </Link>
                    {/* Add more tabs as needed */}
                </nav>
            </div>
        </header>
    );
}

export default Header;