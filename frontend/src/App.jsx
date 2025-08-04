import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Auth0Provider } from '@auth0/auth0-react'

// Context Providers
import { AuthProvider } from './contexts/AuthContext'

// Error handling
import { ErrorBoundary } from './utils/errorReporter.jsx'

// Components
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import NotificationContainer from './components/Notifications/NotificationContainer'

// Pages
import Login from './pages/Login'
import Overview from './pages/Overview'
import CreatePost from './pages/CreatePost'
import Calendar from './pages/Calendar'
import Analytics from './pages/Analytics'
import PerformanceDashboard from './pages/PerformanceDashboard'
import Content from './pages/Content'
import MemoryExplorer from './pages/MemoryExplorer'
import GoalTracking from './pages/GoalTracking'
import Settings from './pages/Settings'
import ErrorLogs from './components/ErrorLogs'

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 2 * 60 * 1000, // 2 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      retry: 2,
      refetchOnWindowFocus: false
    }
  }
})

// Auth0 Configuration with error handling
const auth0Config = {
  domain: import.meta.env.VITE_AUTH0_DOMAIN || 'placeholder.auth0.com',
  clientId: import.meta.env.VITE_AUTH0_CLIENT_ID || 'placeholder-client-id',
  authorizationParams: {
    redirect_uri: window.location.origin,
    audience: import.meta.env.VITE_AUTH0_AUDIENCE || 'https://placeholder.com/api',
    scope: 'openid profile email'
  },
  skipRedirectCallback: true, // Prevent Auth0 from breaking on invalid config
}

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
                <Calendar />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/analytics"
          element={
            <ProtectedRoute>
              <Layout>
                <Analytics />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/performance"
          element={
            <ProtectedRoute>
              <Layout>
                <PerformanceDashboard />
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
          path="/goals"
          element={
            <ProtectedRoute>
              <Layout>
                <GoalTracking />
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
      
      {/* Global Notification System */}
      <NotificationContainer />
    </div>
  )
}

// Safe Auth0 wrapper component
function SafeAuth0Provider({ children }) {
  const hasValidAuth0Config = import.meta.env.VITE_AUTH0_DOMAIN && 
                              import.meta.env.VITE_AUTH0_CLIENT_ID &&
                              import.meta.env.VITE_AUTH0_DOMAIN !== 'placeholder.auth0.com'

  if (!hasValidAuth0Config) {
    console.warn('Auth0 configuration missing or invalid, running in development mode')
    // Return children without Auth0 provider in development
    return children
  }

  return <Auth0Provider {...auth0Config}>{children}</Auth0Provider>
}

function App() {
  return (
    <ErrorBoundary>
      <SafeAuth0Provider>
        <QueryClientProvider client={queryClient}>
          <AuthProvider>
            <Router>
              <AppRoutes />
            </Router>
          </AuthProvider>
        </QueryClientProvider>
      </SafeAuth0Provider>
    </ErrorBoundary>
  )
}

export default App