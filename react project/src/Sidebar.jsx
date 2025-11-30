import React from 'react'

export default function Sidebar({ onNavigate, active }) {
  return (
    <nav className="sidebar">
      <div className="nav-brand">☀️ Kids ScreenTime</div>
      <ul className="nav-list">
        <li className={active === 'home' ? 'active' : ''} onClick={() => onNavigate('home')}>Home</li>
        <li className={active === 'advisor' ? 'active' : ''} onClick={() => onNavigate('advisor')}>Screen Time Advisor</li>
        <li onClick={() => onNavigate('dashboard')}>Dashboard</li>
        <li onClick={() => onNavigate('feedback')}>Feedback</li>
      </ul>
      <footer className="sidebar-foot">Made with ❤️ for Indian families</footer>
    </nav>
  )
}
