import React from 'react';

export default function InputField({ 
  label, 
  type = "text", 
  value, 
  onChange, 
  error, 
  placeholder,
  name,
  id,
  required = false,
  autoComplete,
  options = [] // for select fields
}) {
  const isSelect = type === "select";
  // Generate an id if one wasn't provided
  const inputId = id || `input-${name}-${Math.random().toString(36).substring(2, 9)}`;
  
  // Determine appropriate autocomplete value if not provided
  const getAutoComplete = () => {
    if (autoComplete) return autoComplete;
    
    // Default autocomplete values based on name or type
    if (type === 'password') return 'current-password';
    if (name === 'email' || type === 'email') return 'email';
    if (name === 'username') return 'username';
    if (name === 'confirmPassword') return 'new-password';
    
    return 'off'; // Default to off if we can't determine a good value
  };

  return (
    <div className="mb-4">
      <label htmlFor={inputId} className="block text-sm font-medium text-gray-700 mb-2">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      
      {isSelect ? (
        <select
          id={inputId}
          name={name}
          value={value}
          onChange={onChange}
          className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200 bg-white hover:border-purple-300 ${
            error ? 'border-red-500 focus:ring-red-500 focus:border-red-500' : 'border-gray-300'
          }`}
          required={required}
          autoComplete={getAutoComplete()}
        >
          <option value="">Select {label}</option>
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      ) : (
        <input
          id={inputId}
          type={type}
          name={name}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200 hover:border-purple-300 ${
            error ? 'border-red-500 focus:ring-red-500 focus:border-red-500' : 'border-gray-300'
          }`}
          required={required}
          autoComplete={getAutoComplete()}
        />
      )}
      
      {error && (
        <p className="mt-2 text-sm text-red-600 font-medium flex items-center animate-pulse">
          <svg className="w-4 h-4 mr-1 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          {error}
        </p>
      )}
    </div>
  );
}