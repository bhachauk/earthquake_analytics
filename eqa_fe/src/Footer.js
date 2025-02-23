import React from 'react';
import './Footer.css';

function Footer() {
    return (
        <footer className="fixed-footer">
            <div className="footer-icons">
                <a
                    href="https://github.com/bhachauk/earthquake_analytics"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    <i className="fab fa-github"></i>
                </a>
            </div>
        </footer>
    );
}

export default Footer;