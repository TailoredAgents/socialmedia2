import { useAuth } from '../contexts/AuthContext'
import { useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'

const Login = () => {
  const { loginWithRedirect, isAuthenticated, isLoading, isDemo } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const from = location.state?.from?.pathname || '/'

  useEffect(() => {
    if (isAuthenticated) {
      navigate(from, { replace: true })
    }
  }, [isAuthenticated, navigate, from])

  // In demo mode, automatically redirect since we're always authenticated
  useEffect(() => {
    if (isDemo) {
      navigate(from, { replace: true })
    }
  }, [isDemo, navigate, from])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            AI Social Media Agent
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Demo Mode - No Login Required
          </p>
        </div>
        <div className="mt-8 space-y-6">
          <button
            onClick={() => navigate('/')}
            className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Enter Dashboard
          </button>
          <div className="text-center text-xs text-gray-500">
            Running in demo mode - all features are available for testing
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login