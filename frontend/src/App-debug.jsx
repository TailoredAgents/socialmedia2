import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ErrorBoundary } from './utils/errorReporter.jsx'

// Simple components without Auth0
const SimpleLayout = ({ children }) => (
  <div className="min-h-screen bg-gray-50">
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <h1 className="text-xl font-semibold text-gray-900">
              AI Social Media Agent
            </h1>
          </div>
        </div>
      </div>
    </nav>
    <main className="py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {children}
      </div>
    </main>
  </div>
)

const TestOverview = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
        <p className="text-gray-600 mt-1">
          Testing frontend without Auth0 - Debug Mode
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                <span className="text-white text-sm font-medium">📊</span>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Status</p>
              <p className="text-2xl font-bold text-gray-900">Testing</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                <span className="text-white text-sm font-medium">✅</span>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Frontend</p>
              <p className="text-2xl font-bold text-gray-900">Working</p>
            </div>
          </div>
        </div>
      </div>
      
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Debug Information</h3>
        </div>
        <div className="px-6 py-4 space-y-2">
          <p><strong>Environment:</strong> {import.meta.env.VITE_NODE_ENV || 'undefined'}</p>
          <p><strong>API URL:</strong> {import.meta.env.VITE_API_BASE_URL || 'undefined'}</p>
          <p><strong>Auth0 Domain:</strong> {import.meta.env.VITE_AUTH0_DOMAIN ? '✅ Set' : '❌ Missing'}</p>
          <p><strong>Auth0 Client ID:</strong> {import.meta.env.VITE_AUTH0_CLIENT_ID ? '✅ Set' : '❌ Missing'}</p>
        </div>
      </div>
    </div>
  )
}

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 2 * 60 * 1000,
      cacheTime: 10 * 60 * 1000,
      retry: 2,
      refetchOnWindowFocus: false
    }
  }
})

function AppDebug() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <Router>
          <Routes>
            <Route
              path="*"
              element={
                <SimpleLayout>
                  <TestOverview />
                </SimpleLayout>
              }
            />
          </Routes>
        </Router>
      </QueryClientProvider>
    </ErrorBoundary>
  )
}

export default AppDebug