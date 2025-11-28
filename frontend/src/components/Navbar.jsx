import React from 'react';

const Navbar = () => {
  return (
    <nav className="bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-2xl">📱</span>
            <h1 className="text-2xl font-bold">Screen Time Advisor</h1>
          </div>
          <div className="text-sm">
            <span className="bg-white/20 px-3 py-1 rounded-full">
              For Kids 8-18 years
            </span>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
