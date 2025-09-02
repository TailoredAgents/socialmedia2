import React from 'react'
import { useTheme } from '../contexts/ThemeContext'
import { SunIcon, MoonIcon } from '@heroicons/react/24/outline'

const ThemeToggle = ({ className = '', showLabel = false }) => {
  const { isDarkMode, toggleTheme } = useTheme()

  return (
    <button
      onClick={toggleTheme}
      className={`relative inline-flex items-center justify-center w-10 h-10 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 transition-all duration-200 ${className}`}
      aria-label={`Switch to ${isDarkMode ? 'light' : 'dark'} mode`}
      title={`Switch to ${isDarkMode ? 'light' : 'dark'} mode`}
    >
      <div className="relative">
        {isDarkMode ? (
          <SunIcon className="h-5 w-5 text-yellow-500 transition-transform duration-200 rotate-0 hover:rotate-12" />
        ) : (
          <MoonIcon className="h-5 w-5 text-gray-700 dark:text-gray-300 transition-transform duration-200" />
        )}
      </div>
      
      {showLabel && (
        <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
          {isDarkMode ? 'Light' : 'Dark'}
        </span>
      )}
    </button>
  )
}

export default ThemeToggle