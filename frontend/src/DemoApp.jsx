/*
 * AI Social Media Content Agent - Demo Application
 * Simplified version for demo purposes without Auth0 complexity
 */
import { Suspense, lazy } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { DemoAuthProvider } from './contexts/DemoAuthContext'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import NotificationContainer from './components/Notifications/NotificationContainer'
import { ErrorBoundary, PageErrorBoundary } from './components/ErrorBoundary'
import './styles/accessibility.css'

// Lazy load pages for better performance
const Login = lazy(() => import('./pages/Login'))
const Overview = lazy(() => import('./pages/Overview'))
const Calendar = lazy(() => import('./pages/Calendar'))
const Analytics = lazy(() => import('./pages/Analytics'))
const PerformanceDashboard = lazy(() => import('./pages/PerformanceDashboard'))
const Content = lazy(() => import('./pages/Content'))
const MemoryExplorer = lazy(() => import('./pages/MemoryExplorer'))
const GoalTracking = lazy(() => import('./pages/GoalTracking'))
const Settings = lazy(() => import('./pages/Settings'))

// Loading component
const PageLoadingSpinner = () => (
  <div className="flex items-center justify-center min-h-screen">
    <div className="text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
      <p className="text-gray-600">Loading AI Social Media Agent...</p>
    </div>
  </div>
)

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      cacheTime: 10 * 60 * 1000,
      refetchOnWindowFocus: false,
      // Add retry with exponential backoff for demo stability
      retry: 3,
      retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
    },
  },
})

function DemoApp() {
  return (
    <ErrorBoundary componentName="DemoApp">
      <QueryClientProvider client={queryClient}>
        <DemoAuthProvider>
          <Router>
            <div className="min-h-screen bg-gray-50">
              {/* Skip to main content link */}
              <a href="#main-content" className="skip-link">
                Skip to main content
              </a>
              <NotificationContainer />
              <Suspense fallback={<PageLoadingSpinner />}>
                <Routes>
                  <Route path="/login" element={
                    <PageErrorBoundary pageName="Login">
                      <Login />
                    </PageErrorBoundary>
                  } />
                  <Route 
                    path="/" 
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <PageErrorBoundary pageName="Overview">
                            <Overview />
                          </PageErrorBoundary>
                        </Layout>
                      </ProtectedRoute>
                    } 
                  />
                  <Route 
                    path="/calendar" 
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <PageErrorBoundary pageName="Calendar">
                            <Calendar />
                          </PageErrorBoundary>
                        </Layout>
                      </ProtectedRoute>
                    } 
                  />
                  <Route 
                    path="/analytics" 
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <PageErrorBoundary pageName="Analytics">
                            <Analytics />
                          </PageErrorBoundary>
                        </Layout>
                      </ProtectedRoute>
                    } 
                  />
                  <Route 
                    path="/performance" 
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <PageErrorBoundary pageName="Performance">
                            <PerformanceDashboard />
                          </PageErrorBoundary>
                        </Layout>
                      </ProtectedRoute>
                    } 
                  />
                  <Route 
                    path="/content" 
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <PageErrorBoundary pageName="Content">
                            <Content />
                          </PageErrorBoundary>
                        </Layout>
                      </ProtectedRoute>
                    } 
                  />
                  <Route 
                    path="/memory" 
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <PageErrorBoundary pageName="Memory">
                            <MemoryExplorer />
                          </PageErrorBoundary>
                        </Layout>
                      </ProtectedRoute>
                    } 
                  />
                  <Route 
                    path="/goals" 
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <PageErrorBoundary pageName="Goals">
                            <GoalTracking />
                          </PageErrorBoundary>
                        </Layout>
                      </ProtectedRoute>
                    } 
                  />
                  <Route 
                    path="/settings" 
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <PageErrorBoundary pageName="Settings">
                            <Settings />
                          </PageErrorBoundary>
                        </Layout>
                      </ProtectedRoute>
                    } 
                  />
                </Routes>
              </Suspense>
            </div>
          </Router>
        </DemoAuthProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  )
}

export default DemoApp