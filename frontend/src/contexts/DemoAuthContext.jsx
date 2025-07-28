import React, { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// Demo Auth Provider - simplified for demo purposes
export const DemoAuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [user, setUser] = useState(null)

  useEffect(() => {
    // Simulate loading and auto-login for demo
    const timer = setTimeout(() => {
      setUser({
        name: 'Demo User',
        email: 'demo@aisocialagent.com',
        picture: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face'
      })
      setIsAuthenticated(true)
      setIsLoading(false)
    }, 1000)

    return () => clearTimeout(timer)
  }, [])

  const login = () => {
    setIsLoading(true)
    setTimeout(() => {
      setUser({
        name: 'Demo User',
        email: 'demo@aisocialagent.com',
        picture: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&face'
      })
      setIsAuthenticated(true)
      setIsLoading(false)
    }, 500)
  }

  const logout = () => {
    setUser(null)
    setIsAuthenticated(false)
  }

  const getAccessTokenSilently = async () => {
    return 'demo_access_token'
  }

  const value = {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    getAccessTokenSilently,
    accessToken: 'demo_access_token'
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}