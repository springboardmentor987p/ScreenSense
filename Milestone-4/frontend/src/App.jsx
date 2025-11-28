import React, { useState } from 'react';
import Navbar from './components/Navbar';
import InputForm from './components/InputForm';
import ResultsDisplay from './components/ResultsDisplay';
import PowerBIDashboard from './components/PowerBIDashboard';
import { analyzeScreenTime } from './services/api';
import './App.css';
import './index.css';

function App() {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('form'); // 'form' or 'dashboard'

  const handleSubmit = async (formData) => {
    setLoading(true);
    setError(null);
    try {
      const result = await analyzeScreenTime(formData);
      setAnalysis(result);
    } catch (err) {
      setError('Failed to analyze. Please check if the backend is running.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      {/* Navbar - NOT aligned */}
      <Navbar />
      
      <div className="container mx-auto px-4 py-8">
        {/* Tab Navigation - NOT aligned (centered) */}
        <div className="flex justify-center mb-6 space-x-4">
          <button
            onClick={() => setActiveTab('form')}
            className={`px-6 py-3 rounded-lg font-semibold transition ${
              activeTab === 'form'
                ? 'bg-blue-600 text-white shadow-lg'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            📝 Home 
          </button>
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`px-6 py-3 rounded-lg font-semibold transition ${
              activeTab === 'dashboard'
                ? 'bg-blue-600 text-white shadow-lg'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            📊 View Dashboard
          </button>
        </div>

        {/* Error Message - aligned at 37.5% (same as input) */}
        {error && (
          <div className="input-aligned">
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg mb-6">
              ❌ {error}
            </div>
          </div>
        )}

        {/* Content Based on Active Tab */}
        {activeTab === 'form' ? (
          <div className="grid grid-cols-1 gap-6">
            {/* InputForm - aligned at 37.5% */}
            <div className="input-aligned">
              <InputForm onSubmit={handleSubmit} loading={loading} />
            </div>
            
            {/* ResultsDisplay - Summary at 20%, others full width */}
            {analysis && <ResultsDisplay analysis={analysis} summaryAligned={true} />}
          </div>
        ) : (
          // Dashboard - NOT aligned (centered)
          <PowerBIDashboard />
        )}
      </div>

      {/* Footer - NOT aligned (centered) */}
      <footer className="bg-white border-t mt-12 py-6">
        <div className="container mx-auto px-4 text-center text-gray-600">
          <p>🎯 Screen Time Recommendation System | Built with React + FastAPI</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
