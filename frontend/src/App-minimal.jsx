import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ErrorBoundary } from './utils/errorReporter.jsx'

// Simple test component
function SimpleOverview() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">
        AI Social Media Agent - Test Mode
      </h1>
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">System Status</h2>
        <div className="space-y-2">
          <p className="text-green-600">✅ Frontend: Running</p>
          <p className="text-blue-600">ℹ️ Backend: Testing connection...</p>
          <p className="text-gray-600">📊 This is a minimal test version</p>
        </div>
      </div>
    </div>
  )
}

// Simple routing without complex dependencies
function AppMinimal() {
  return (
    <ErrorBoundary>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Routes>
            <Route path="*" element={<SimpleOverview />} />
          </Routes>
        </div>
      </Router>
    </ErrorBoundary>
  )
}

export default AppMinimal