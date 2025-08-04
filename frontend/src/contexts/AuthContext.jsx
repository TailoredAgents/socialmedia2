import React, { createContext, useContext, useState } from 'react'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  // Simple authentication state without Auth0
  const [user, setUser] = useState({
    id: 'demo-user-1',
    name: 'Demo User',
    email: 'demo@example.com',
    picture: 'https://via.placeholder.com/40x40?text=DU'
  })
  const [isAuthenticated, setIsAuthenticated] = useState(true) // Always authenticated in demo mode
  const [isLoading, setIsLoading] = useState(false)
  const [accessToken, setAccessToken] = useState('demo-token')

  // Mock authentication functions
  const loginWithRedirect = () => {
    console.log('Login functionality - running in demo mode')
    setIsAuthenticated(true)
  }

  const logout = () => {
    console.log('Logout functionality - running in demo mode')
    setIsAuthenticated(false)
    setUser(null)
    setAccessToken(null)
  }

  const getAccessTokenSilently = () => {
    return Promise.resolve(accessToken)
  }

  const contextValue = {
    user,
    isAuthenticated,
    isLoading,
    accessToken,
    loginWithRedirect,
    logout,
    getAccessTokenSilently,
    // Additional helper methods
    updateUser: setUser,
    setAuthenticated: setIsAuthenticated,
    isDemo: true // Flag to indicate this is demo mode
  }

  return <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>
}