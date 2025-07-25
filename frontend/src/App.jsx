import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Auth0Provider } from '@auth0/auth0-react'
import { AuthProvider } from './contexts/AuthContext'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import NotificationContainer from './components/Notifications/NotificationContainer'
import Login from './pages/Login'
import Overview from './pages/Overview'
import Calendar from './pages/Calendar'
import Analytics from './pages/Analytics'
import PerformanceDashboard from './pages/PerformanceDashboard'
import Content from './pages/Content'
import MemoryExplorer from './pages/MemoryExplorer'
import GoalTracking from './pages/GoalTracking'
import Settings from './pages/Settings'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      cacheTime: 10 * 60 * 1000,
      refetchOnWindowFocus: false,
    },
  },
})

function App() {
  return (
    <Auth0Provider
      domain={import.meta.env.VITE_AUTH0_DOMAIN}
      clientId={import.meta.env.VITE_AUTH0_CLIENT_ID}
      authorizationParams={{
        redirect_uri: window.location.origin,
        audience: import.meta.env.VITE_AUTH0_AUDIENCE,
        scope: 'openid profile email'
      }}
      useRefreshTokens={true}
      cacheLocation="localstorage"
    >
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <Router>
            <div className="min-h-screen bg-gray-50">
              <NotificationContainer />
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
              </Routes>
            </div>
          </Router>
        </AuthProvider>
      </QueryClientProvider>
    </Auth0Provider>
  )
}

export default App