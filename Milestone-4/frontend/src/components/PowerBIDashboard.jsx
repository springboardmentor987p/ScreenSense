import React, { useState } from 'react';
import dashboard1 from '../assets/dashboard-1-overview.png';
import dashboard2 from '../assets/dashboard-2-analysis.png';
import dashboard3 from '../assets/dashboard-3-health.png';
import dashboard4 from '../assets/dashboard-4-devices.png';
import '../App.css';

const PowerBIDashboard = () => {
  const [currentPage, setCurrentPage] = useState(1);

  const dashboards = [
    {
      id: 1,
      img: dashboard1,
      title: "Overview Dashboard on Indian Kids' Screen Time",
      description: "Key metrics and summary statistics including total kids analyzed, average screen time, % exceeding limits, and most common health impacts."
    },
    {
      id: 2,
      img: dashboard2,
      title: "Screen Time Deep Analysis",
      description: "Detailed breakdown by age groups, gender distribution, device usage patterns, and urban vs rural comparisons."
    },
    {
      id: 3,
      img: dashboard3,
      title: "Health Impacts Analysis",
      description: "Health correlations showing most common health issues among kids including poor sleep, eye strain, anxiety, and obesity risk patterns."
    },
    {
      id: 4,
      img: dashboard4,
      title: "Devices & Population Insights",
      description: "Device usage patterns across smartphones, laptops, TVs, and tablets with gender-based distribution analysis."
    }
  ];

  const totalPages = dashboards.length;

  const goToPage = (pageNum) => {
    setCurrentPage(pageNum);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const nextPage = () => {
    if (currentPage < totalPages) {
      goToPage(currentPage + 1);
    }
  };

  const prevPage = () => {
    if (currentPage > 1) {
      goToPage(currentPage - 1);
    }
  };

  const currentDashboard = dashboards[currentPage - 1];

  return (
    <div className="dashboard-container">
      {/* Page Header - centered */}
      <div className="page-header" style={{ textAlign: 'center' }}>
        <h1 className="page-title"> Power BI Dashboard - Indian Kids Screen Time</h1>
        <p style={{ color: '#fff', marginBottom: '24px' }}>
          Comprehensive analysis of screen time patterns, health impacts, and demographic insights.
        </p>
      </div>

      {/* Dashboard Display */}
      <div className="dashboard panel">
        {/* Title and description - CENTERED */}
        <div style={{ textAlign: 'center', marginBottom: '20px' }}>
          <h2 style={{ color: '#667eea', marginBottom: '12px' }}>
            {currentDashboard.title}
          </h2>
          <p style={{ color: '#64748b', fontSize: '1.05em' }}>
            {currentDashboard.description}
          </p>
        </div>

        {/* Dashboard image - centered */}
        <div className="dashboard-image-container">
          <img
            src={currentDashboard.img}
            alt={currentDashboard.title}
            className="dashboard-screenshot"
          />
        </div>

        {/* Navigation: Previous/Next + Page Numbers - centered in single line */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center',
          gap: '20px',
          marginTop: '24px',
          flexWrap: 'wrap'
        }}>
          <button
            className="btn"
            onClick={prevPage}
            disabled={currentPage === 1}
            style={{
              opacity: currentPage === 1 ? 0.5 : 1,
              cursor: currentPage === 1 ? 'not-allowed' : 'pointer'
            }}
          >
            ← Previous
          </button>

          {/* Numbered pagination buttons */}
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            {dashboards.map((dash) => (
              <button
                key={dash.id}
                className={`pagination-btn ${currentPage === dash.id ? 'active' : ''}`}
                onClick={() => goToPage(dash.id)}
                title={dash.title}
              >
                {dash.id}
              </button>
            ))}
            <span style={{ color: '#fff', fontWeight: '500', marginLeft: '8px' }}>
              Page {currentPage} of {totalPages}
            </span>
          </div>

          <button
            className="btn"
            onClick={nextPage}
            disabled={currentPage === totalPages}
            style={{
              opacity: currentPage === totalPages ? 0.5 : 1,
              cursor: currentPage === totalPages ? 'not-allowed' : 'pointer'
            }}
          >
            Next →
          </button>
        </div>
      </div>

      {/* Download Section */}
      <div className="dashboard panel" style={{ marginTop: '32px' }}>
          <h3 style={{ color: '#667eea', marginBottom: '16px' }}>
            📥 Download Interactive Report
          </h3>
          <p style={{ textAlign:'center', color: '#64748b', marginBottom: '20px' }}>
            Get the full Power BI report with interactive filters and drill-down capabilities.
          </p>
        
        {/* Download button - centered */}
        <div style={{ textAlign: 'center' }}>
          <a
            href="/indian-kids-screen-time.pbix"
            download
            className="btn"
            style={{ display: 'inline-block', textDecoration: 'none' }}
          >
            ⬇️ Download Power BI Report (.pbix)
          </a>
        </div>

        {/* Instructions - aligned at 38% */}
        <div className="input-aligned" style={{ marginTop: '24px' }}>
          <h4 style={{ color: '#667eea', marginBottom: '12px' }}>
            📋 How to Use the Downloaded Report:
          </h4>
          <ul style={{ color: '#64748b', lineHeight: '1.8' }}>
            <li>1. Download the .pbix file above.</li>
            <li>2. Install Power BI Desktop (free) from Microsoft.</li>
            <li>3. Open the .pbix file in Power BI Desktop.</li>
            <li>4. Interact with filters, drill down into data, and explore insights.</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default PowerBIDashboard;
