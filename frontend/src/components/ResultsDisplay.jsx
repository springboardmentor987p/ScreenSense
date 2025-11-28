import React, { useState } from 'react';

const ResultsDisplay = ({ analysis, summaryAligned = false }) => {
  const [activeTab, setActiveTab] = useState('summary');

  if (!analysis) return null;

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'Healthy': return 'bg-green-100 text-green-800 border-green-300';
      case 'Moderate': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'High': return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'Critical': return 'bg-red-100 text-red-800 border-red-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 space-y-6">
      {/* Analysis Results heading - Full width */}
      <h2 className="text-2xl font-bold text-gray-800">📊 Analysis Results</h2>

      {/* Tab Navigation - Full width */}
      <div className="flex space-x-2 border-b">
        <button
          onClick={() => setActiveTab('summary')}
          className={`px-4 py-2 font-semibold transition ${
            activeTab === 'summary'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          📋 Summary
        </button>
        <button
          onClick={() => setActiveTab('comparison')}
          className={`px-4 py-2 font-semibold transition ${
            activeTab === 'comparison'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          📊 Comparison Chart
        </button>
        <button
          onClick={() => setActiveTab('dashboard')}
          className={`px-4 py-2 font-semibold transition ${
            activeTab === 'dashboard'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          📈 Full Dashboard
        </button>
        <button
          onClick={() => window.location.reload()}
          className="bg-green-600 text-white px-6 py-3 rounded-lg"
        >
          🔄 Start New Analysis
        </button>
      </div>

      {/* Summary Tab - ONLY THIS gets 35% alignment */}
      {activeTab === 'summary' && (
        <div className={summaryAligned ? 'content-aligned' : ''}>
          <div className="space-y-6">
            {/* User Profile */}
            <div className="bg-blue-50 rounded-lg p-4">
              <h3 className="font-semibold text-lg mb-3">👤 User Profile</h3>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div><span className="font-medium">Age:</span> {analysis.age} years ({analysis.age_group})</div>
                <div><span className="font-medium">Gender:</span> {analysis.gender}</div>
                <div><span className="font-medium">Device:</span> {analysis.device}</div>
                <div><span className="font-medium">Location:</span> {analysis.location}</div>
              </div>
            </div>

            {/* Screen Time Analysis */}
            <div className="bg-purple-50 rounded-lg p-4">
              <h3 className="font-semibold text-lg mb-3">📱 Screen Time Breakdown</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>Educational:</span>
                  <span className="font-semibold">{analysis.educational_hours.toFixed(1)} hrs/day</span>
                </div>
                <div className="flex justify-between">
                  <span>Recreational:</span>
                  <span className="font-semibold">{analysis.recreational_hours.toFixed(1)} hrs/day</span>
                </div>
                <div className="flex justify-between border-t pt-2">
                  <span className="font-semibold">Total:</span>
                  <span className="font-bold text-lg">{analysis.screen_time.toFixed(1)} hrs/day</span>
                </div>
                <div className="flex justify-between">
                  <span>Recommended Limit:</span>
                  <span className="font-semibold text-blue-600">{analysis.recommended_limit.toFixed(1)} hrs/day</span>
                </div>
                <div className="flex justify-between">
                  <span>Edu/Rec Ratio:</span>
                  <span className="font-semibold">{analysis.edu_rec_ratio.toFixed(2)}</span>
                </div>
              </div>
            </div>

            {/* Severity Status */}
            <div className={`rounded-lg p-4 border-2 ${getSeverityColor(analysis.severity)}`}>
              <h3 className="font-semibold text-lg mb-2">⚡ Status</h3>
              <p className="text-2xl font-bold">{analysis.severity}</p>
              {analysis.exceeds_by > 0 ? (
                <p className="mt-2">⚠️ Exceeds by: <strong>{analysis.exceeds_by.toFixed(1)} hours/day</strong></p>
              ) : (
                <p className="mt-2">✅ Within limit by: <strong>{Math.abs(analysis.exceeds_by).toFixed(1)} hours/day</strong></p>
              )}
            </div>

            {/* Health Impacts */}
            {analysis.health_impacts && analysis.health_impacts.length > 0 && (
              <div className="bg-red-50 rounded-lg p-4">
                <h3 className="font-semibold text-lg mb-2">🏥 Reported Health Impacts</h3>
                <div className="flex flex-wrap gap-2">
                  {analysis.health_impacts.map((impact, idx) => (
                    <span key={idx} className="bg-red-200 text-red-800 px-3 py-1 rounded-full text-sm">
                      {impact}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Recommendations */}
            <div className="bg-green-50 rounded-lg p-4">
              <h3 className="font-semibold text-lg mb-3">💡 Personalized Recommendations</h3>
              <ul className="space-y-2">
                {analysis.recommendations.map((rec, idx) => (
                  <li key={idx} className="text-sm text-gray-700 flex items-start">
                    <span className="mr-2">•</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Comparison Chart Tab - Full width, centered */}
      {activeTab === 'comparison' && analysis.comparison_chart && (
        <div className="space-y-4" style={{ maxWidth: '100%', textAlign: 'center' }}>
          <h3 className="font-semibold text-lg">📊 Peer to Peer Comparison Chart</h3>
          <img 
            src={analysis.comparison_chart} 
            alt="Peer Comparison Chart"
            className="w-full rounded-lg border shadow-md"
            style={{ maxWidth: '100%', margin: '0 auto', display: 'block' }}
          />
          <p className="text-sm text-gray-600">
            This chart compares your child's screen time with various peer groups.
          </p>
        </div>
      )}

      {/* Dashboard Tab - Full width, centered */}
      {activeTab === 'dashboard' && analysis.dashboard_chart && (
        <div className="space-y-4" style={{ maxWidth: '100%', textAlign: 'center' }}>
          <h3 className="font-semibold text-lg">📈 Complete Analysis Dashboard</h3>
          <img 
            src={analysis.dashboard_chart} 
            alt="Full Dashboard"
            className="w-full rounded-lg border shadow-md"
            style={{ maxWidth: '100%', margin: '0 auto', display: 'block' }}
          />
          <p className="text-sm text-gray-600">
            Comprehensive 6-panel dashboard showing detailed analysis of screen time patterns.
          </p>
        </div>
      )}
    </div>
  );
};

export default ResultsDisplay;
