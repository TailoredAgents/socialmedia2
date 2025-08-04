import React, { createContext, useContext, useEffect, useState } from 'react'
import { useAuth0 } from '@auth0/auth0-react'
import { error as logError } from '../utils/logger.js'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  // Check if Auth0 is available
  let auth0Data
  try {
    auth0Data = useAuth0()
  } catch (error) {
    // Auth0 not available, provide mock data for development
    auth0Data = {
      user: null,
      isAuthenticated: false,
      isLoading: false,
      loginWithRedirect: () => console.log('Auth0 not configured'),
      logout: () => console.log('Auth0 not configured'),
      getAccessTokenSilently: () => Promise.resolve(null),
      getIdTokenClaims: () => Promise.resolve(null)
    }
  }
  
  const {
    user,
    isAuthenticated,
    isLoading,
    loginWithRedirect,
    logout,
    getAccessTokenSilently,
    getIdTokenClaims
  } = auth0Data
  
  const [accessToken, setAccessToken] = useState(null)
  const [userProfile, setUserProfile] = useState(null)

  useEffect(() => {
    const getToken = async () => {
      if (isAuthenticated) {
        try {
          const token = await getAccessTokenSilently({
            authorizationParams: {
              audience: import.meta.env.VITE_AUTH0_AUDIENCE,
              scope: 'openid profile email'
            }
          })
          setAccessToken(token)
          
          const claims = await getIdTokenClaims()
          setUserProfile({
            ...user,
            claims
          })
        } catch (error) {
          logError('Error getting access token:', error)
        }
      }
    }

    getToken()
  }, [isAuthenticated, getAccessTokenSilently, getIdTokenClaims, user])

  const login = () => {
    loginWithRedirect({
      authorizationParams: {
        audience: import.meta.env.VITE_AUTH0_AUDIENCE,
        scope: 'openid profile email'
      }
    })
  }

  const logoutUser = () => {
    logout({
      logoutParams: {
        returnTo: window.location.origin
      }
    })
  }

  const refreshToken = async () => {
    try {
      const token = await getAccessTokenSilently({
        authorizationParams: {
          audience: import.meta.env.VITE_AUTH0_AUDIENCE,
          scope: 'openid profile email'
        },
        cacheMode: 'off'
      })
      setAccessToken(token)
      return token
    } catch (error) {
      logError('Error refreshing token:', error)
      throw error
    }
  }

  const value = {
    user: userProfile,
    isAuthenticated,
    isLoading,
    accessToken,
    login,
    logout: logoutUser,
    refreshToken,
    hasPermission: (permission) => {
      return userProfile?.claims?.permissions?.includes(permission) || false
    },
    hasRole: (role) => {
      return userProfile?.claims?.roles?.includes(role) || false
    }
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}