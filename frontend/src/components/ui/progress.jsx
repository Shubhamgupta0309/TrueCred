import React from 'react';

const Progress = ({ value = 0, className = '' }) => {
  const clampedValue = Math.min(100, Math.max(0, value));
  
  return (
    <div className={`w-full bg-gray-200 rounded-full overflow-hidden ${className}`}>
      <div
        className="bg-gradient-to-r from-purple-500 to-purple-600 h-full transition-all duration-300 ease-out"
        style={{ width: `${clampedValue}%` }}
        role="progressbar"
        aria-valuenow={clampedValue}
        aria-valuemin="0"
        aria-valuemax="100"
      />
    </div>
  );
};

export { Progress };
