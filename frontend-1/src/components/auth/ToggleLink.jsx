import React from 'react';

export default function ToggleLink({ isLogin, onToggle }) {
  return (
    <div className="text-center mt-6">
      <p className="text-gray-600">
        {isLogin ? "Don't have an account? " : "Already have an account? "}
        <button
          onClick={onToggle}
          className="font-medium text-purple-600 hover:text-purple-800 transition-colors duration-200 underline underline-offset-4 hover:underline-offset-2"
        >
          {isLogin ? 'Sign up here' : 'Sign in here'}
        </button>
      </p>
    </div>
  );
}