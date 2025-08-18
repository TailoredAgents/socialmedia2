import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

// Context Providers
import { AuthProvider } from './contexts/AuthContext'
import { WebSocketProvider } from './contexts/WebSocketContext'

// Error handling
import { ErrorBoundary } from './utils/errorReporter.jsx'

// Components
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import RealTimeNotificationContainer from './components/Notifications/RealTimeNotificationContainer'

// Pages
import Login from './pages/Login'
import Overview from './pages/Overview'
import CreatePost from './pages/CreatePost'
import Scheduler from './pages/Scheduler'
import Content from './pages/Content'
import MemoryExplorer from './pages/MemoryExplorer'
import Settings from './pages/Settings'
import ErrorLogs from './components/ErrorLogs'

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 10 * 60 * 1000, // 10 minutes - keep cached longer
      cacheTime: 30 * 60 * 1000, // 30 minutes
      retry: 0, // Disable retries to prevent CORS cascades
      refetchOnWindowFocus: false,
      refetchOnReconnect: false, // Don't refetch when reconnecting
      refetchInterval: false, // Disable automatic refetching
      enabled: true // Can be controlled per query
    }
  }
})

// No authentication configuration needed

function AppRoutes() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout>
                <Overview />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/create-post"
          element={
            <ProtectedRoute>
              <Layout>
                <CreatePost />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/calendar"
          element={
            <ProtectedRoute>
              <Layout>
                <Scheduler />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/content"
          element={
            <ProtectedRoute>
              <Layout>
                <Content />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/memory"
          element={
            <ProtectedRoute>
              <Layout>
                <MemoryExplorer />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <Layout>
                <Settings />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/error-logs"
          element={
            <ProtectedRoute>
              <Layout>
                <ErrorLogs />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      
      {/* Real-time Notification System */}
      <RealTimeNotificationContainer />
    </div>
  )
}

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <WebSocketProvider>
            <Router>
              <AppRoutes />
            </Router>
          </WebSocketProvider>
        </AuthProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  )
}

export default App