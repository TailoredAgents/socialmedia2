import React, { Suspense, lazy, useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Tooltip } from 'react-tooltip'
import './App.css'

// Lazy load components for code splitting
const Overview = lazy(() => import('./components/Overview'))
const ContentCalendar = lazy(() => import('./components/ContentCalendar'))
const AnalyticsHub = lazy(() => import('./components/AnalyticsHub'))
const MemoryExplorer = lazy(() => import('./components/MemoryExplorer'))
const Settings = lazy(() => import('./components/Settings'))
const AlertsFeed = lazy(() => import('./components/AlertsFeed'))

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    },
  },
})

// Sidebar Navigation Component
const Sidebar = ({ currentPage, setCurrentPage, darkMode }) => {
  const navigationItems = [
    { id: 'overview', name: 'Overview', icon: '🏠' },
    { id: 'calendar', name: 'Content Calendar', icon: '📅' },
    { id: 'analytics', name: 'Analytics Hub', icon: '📊' },
    { id: 'memory', name: 'Memory Explorer', icon: '🧠' },
    { id: 'alerts', name: 'Alerts Feed', icon: '🔔' },
    { id: 'settings', name: 'Settings', icon: '⚙️' },
  ]

  return (
    <div className={`fixed left-0 top-0 h-full w-64 backdrop-blur-md ${
      darkMode ? 'bg-gray-900/90' : 'bg-white/90'
    } border-r border-gray-200/20 z-40`}>
      {/* Logo Section */}
      <div className="p-6 border-b border-gray-200/20">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-r from-teal-600 to-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">TA</span>
          </div>
          <div>
            <h1 className={`text-lg font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
              Tailored Agents
            </h1>
            <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
              Custom AI for Your Social Media Success
            </p>
          </div>
        </div>
      </div>

      {/* Navigation Items */}
      <nav className="p-4 space-y-2">
        {navigationItems.map((item) => (
          <motion.button
            key={item.id}
            onClick={() => setCurrentPage(item.id)}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all ${
              currentPage === item.id
                ? 'bg-gradient-to-r from-teal-600 to-blue-600 text-white shadow-lg'
                : darkMode
                ? 'text-gray-300 hover:bg-gray-800 hover:text-white'
                : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
            }`}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            data-tooltip-id="nav-tooltip"
            data-tooltip-content={item.name}
          >
            <span className="text-xl">{item.icon}</span>
            <span className="font-medium">{item.name}</span>
          </motion.button>
        ))}
      </nav>
    </div>
  )
}

// Header Component
const Header = ({ darkMode, setDarkMode, searchQuery, setSearchQuery }) => {
  return (
    <header className={`fixed top-0 right-0 left-64 h-16 backdrop-blur-md ${
      darkMode ? 'bg-gray-900/90' : 'bg-white/90'
    } border-b border-gray-200/20 z-30`}>
      <div className="flex items-center justify-between px-6 py-4">
        {/* Search Bar */}
        <div className="flex-1 max-w-md">
          <div className="relative">
            <input
              type="text"
              placeholder="Search content, analytics, or settings..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className={`w-full pl-10 pr-4 py-2 rounded-lg border ${
                darkMode
                  ? 'bg-gray-800 border-gray-700 text-white placeholder-gray-400'
                  : 'bg-gray-50 border-gray-300 text-gray-900 placeholder-gray-500'
              } focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent`}
            />
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <span className="text-gray-400">🔍</span>
            </div>
          </div>
        </div>

        {/* Header Actions */}
        <div className="flex items-center space-x-4">
          {/* Dark Mode Toggle */}
          <button
            onClick={() => setDarkMode(!darkMode)}
            className={`p-2 rounded-lg transition-colors ${
              darkMode
                ? 'bg-gray-800 text-yellow-400 hover:bg-gray-700'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
            data-tooltip-id="header-tooltip"
            data-tooltip-content={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {darkMode ? '☀️' : '🌙'}
          </button>

          {/* User Profile */}
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-r from-teal-600 to-blue-600 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-medium">U</span>
            </div>
            <span className={`text-sm font-medium ${darkMode ? 'text-white' : 'text-gray-900'}`}>
              User
            </span>
          </div>
        </div>
      </div>
    </header>
  )
}

// Loading Component
const LoadingSpinner = ({ darkMode }) => (
  <div className="flex items-center justify-center h-64">
    <motion.div
      className="w-16 h-16 border-4 border-teal-200 border-t-teal-600 rounded-full"
      animate={{ rotate: 360 }}
      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
    />
  </div>
)

// Footer Component
const Footer = ({ darkMode }) => (
  <footer className={`mt-12 py-6 border-t ${
    darkMode ? 'border-gray-800 text-gray-400' : 'border-gray-200 text-gray-600'
  }`}>
    <div className="text-center">
      <p className="text-sm">
        Powered by <span className="font-semibold text-teal-600">Tailored Agents</span> © 2025
      </p>
      <p className="text-xs mt-1">
        Enterprise AI Social Media Management Platform
      </p>
    </div>
  </footer>
)

// Main App Component
function App() {
  const [currentPage, setCurrentPage] = useState('overview')
  const [darkMode, setDarkMode] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  // Apply dark mode to document
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [darkMode])

  const renderCurrentPage = () => {
    const pageProps = { darkMode, searchQuery }
    
    switch (currentPage) {
      case 'overview':
        return <Overview {...pageProps} />
      case 'calendar':
        return <ContentCalendar {...pageProps} />
      case 'analytics':
        return <AnalyticsHub {...pageProps} />
      case 'memory':
        return <MemoryExplorer {...pageProps} />
      case 'alerts':
        return <AlertsFeed {...pageProps} />
      case 'settings':
        return <Settings {...pageProps} />
      default:
        return <Overview {...pageProps} />
    }
  }

  return (
    <QueryClientProvider client={queryClient}>
      <div className={`min-h-screen transition-colors ${
        darkMode ? 'bg-gray-900 text-white' : 'bg-gray-50 text-gray-900'
      }`}>
        {/* Sidebar */}
        <Sidebar 
          currentPage={currentPage} 
          setCurrentPage={setCurrentPage} 
          darkMode={darkMode} 
        />

        {/* Header */}
        <Header 
          darkMode={darkMode} 
          setDarkMode={setDarkMode}
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
        />

        {/* Main Content */}
        <main className="ml-64 pt-16 min-h-screen">
          <div className="p-6">
            <Suspense fallback={<LoadingSpinner darkMode={darkMode} />}>
              <motion.div
                key={currentPage}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                {renderCurrentPage()}
              </motion.div>
            </Suspense>
            
            <Footer darkMode={darkMode} />
          </div>
        </main>

        {/* Tooltips */}
        <Tooltip id="nav-tooltip" place="right" />
        <Tooltip id="header-tooltip" place="bottom" />
      </div>
    </QueryClientProvider>
  )
}

export default App