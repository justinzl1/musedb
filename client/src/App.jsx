import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import ViewAllData from './pages/ViewAllData';
import Search from './pages/Search';
import Insert from './pages/Insert';
import Delete from './pages/Delete';
import './App.css';

// Navigation component
function Navigation() {
  const location = useLocation();

  const navLinks = [
    { path: '/', label: 'View All Data', exact: true },
    { path: '/search', label: 'Search' },
    { path: '/insert', label: 'Insert' },
    { path: '/delete', label: 'Delete' },
  ];
  // Render navigation links
  return (
    <nav className="navigation">
      <ul className="nav-list">
        {navLinks.map((link) => {
          const isActive = link.exact
            ? location.pathname === link.path
            : location.pathname.startsWith(link.path);
          return (
            <li key={link.path}>
              <Link
                to={link.path}
                className={isActive ? 'nav-link active' : 'nav-link'}
              >
                {link.label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="app">
        <div className="app-content-wrapper">
          <header className="app-header">
            <h1>MuseDB Database Manager</h1>
            <p>Manage your music database</p>
          </header>
          <Navigation />
          <Routes>
            <Route path="/" element={<ViewAllData />} />
            <Route path="/search" element={<Search />} />
            <Route path="/insert" element={<Insert />} />
            <Route path="/delete" element={<Delete />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
