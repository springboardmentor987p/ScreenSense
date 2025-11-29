import React, { useState } from 'react';
import { ClipLoader } from 'react-spinners';
const InputForm = ({ onSubmit, loading }) => {
  const [formData, setFormData] = useState({
    age: 12,
    gender: 'Male',
    device: 'Smartphone',
    location: 'Urban',
    educational_hours: 2,
    recreational_hours: 3,
    health_impacts: []
  });

  const devices = ['Smartphone', 'Laptop', 'TV', 'Tablet'];
  const healthOptions = ['Poor Sleep', 'Eye Strain', 'Anxiety', 'Obesity Risks', 'None'];

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    if (type === 'checkbox') {
      setFormData(prev => ({
        ...prev,
        health_impacts: checked 
          ? [...prev.health_impacts, value]
          : prev.health_impacts.filter(h => h !== value)
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: type === 'number' ? parseFloat(value || 0) : value
      }));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">📋 Enter Details</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Age */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            📅 Age (8-18 years)
          </label>
          <input
            type="number"
            name="age"
            min="8"
            max="18"
            value={formData.age}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
        </div>

        {/* Gender */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            👤 Gender
          </label>
          <select
            name="gender"
            value={formData.gender}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="Male">Male</option>
            <option value="Female">Female</option>
          </select>
        </div>

        {/* Device */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            📱 Primary Device
          </label>
          <select
            name="device"
            value={formData.device}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {devices.map(device => (
              <option key={device} value={device}>{device}</option>
            ))}
          </select>
        </div>

        {/* Location */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            🏙️ Location
          </label>
          <select
            name="location"
            value={formData.location}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="Urban">Urban</option>
            <option value="Rural">Rural</option>
          </select>
        </div>

        {/* Educational Hours */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            📚 Educational Screen Time (hours/day)
          </label>
          <input
            type="number"
            name="educational_hours"
            min="0"
            max="24"
            step="0.01"
            value={formData.educational_hours}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
        </div>

        {/* Recreational Hours */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            🎮 Recreational Screen Time (hours/day)
          </label>
          <input
            type="number"
            name="recreational_hours"
            min="0"
            max="24"
            step="0.01"
            value={formData.recreational_hours}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
        </div>

        {/* Health Impacts */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            🏥 Health Impacts (select all that apply)
          </label>
          <div className="space-y-2">
            {healthOptions.map(option => (
              <label key={option} className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  value={option}
                  checked={formData.health_impacts.includes(option)}
                  onChange={handleChange}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">{option}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? <ClipLoader color="#fff" size={20} /> : '🔍 Get Recommendations'}
        </button>
      </form>
    </div>
  );
};

export default InputForm;
