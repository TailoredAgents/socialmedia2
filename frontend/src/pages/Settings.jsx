import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useEnhancedApi } from '../hooks/useEnhancedApi'
import { useNotifications } from '../hooks/useNotifications'
import { error as logError } from '../utils/logger.js'
import {
  UserIcon,
  KeyIcon,
  LinkIcon,
  BellIcon,
  CogIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'

export default function Settings() {
  const { user } = useAuth()
  const { api, connectionStatus, checkApiHealth } = useEnhancedApi()
  const { showSuccess, showError } = useNotifications()
  
  const [isLoading, setIsLoading] = useState(false)
  const [apiHealth, setApiHealth] = useState(null)
  
  const [settings, setSettings] = useState({
    notifications: {
      goalMilestones: true,
      contentPublished: true,
      workflowComplete: true,
      systemAlerts: true,
      apiErrors: true
    },
    automation: {
      dailyWorkflows: true,
      autoOptimization: false,
      smartScheduling: true,
      contentGeneration: true
    },
    platforms: {
      twitter: { connected: false, username: '' },
      linkedin: { connected: false, username: '' },
      instagram: { connected: false, username: '' },
      facebook: { connected: false, username: '' }
    }
  })

  // Check API health on component mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health = await checkApiHealth()
        setApiHealth(health)
      } catch (error) {
        logError('Health check failed:', error)
      }
    }
    
    checkHealth()
    // Check health every 30 seconds
    const interval = setInterval(checkHealth, 30000)
    return () => clearInterval(interval)
  }, [checkApiHealth])

  const handleNotificationChange = (key) => {
    setSettings(prev => ({
      ...prev,
      notifications: {
        ...prev.notifications,
        [key]: !prev.notifications[key]
      }
    }))
    showSuccess('Notification preferences updated')
  }

  const handleAutomationChange = (key) => {
    setSettings(prev => ({
      ...prev,
      automation: {
        ...prev.automation,
        [key]: !prev.automation[key]
      }
    }))
    showSuccess('Automation settings updated')
  }

  const handleTestNotification = () => {
    showSuccess('Test notification sent successfully!', 'Test Notification')
  }

  const handleClearCache = async () => {
    try {
      setIsLoading(true)
      await api.clearCache?.()
      showSuccess('Cache cleared successfully')
    } catch (error) {
      showError('Failed to clear cache')
    } finally {
      setIsLoading(false)
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'connected':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />
      case 'disconnected':
        return <XCircleIcon className="h-5 w-5 text-red-500" />
      case 'reconnecting':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />
      default:
        return <ExclamationTriangleIcon className="h-5 w-5 text-gray-500" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'connected':
        return 'text-green-600'
      case 'disconnected':
        return 'text-red-600'
      case 'reconnecting':
        return 'text-yellow-600'
      default:
        return 'text-gray-600'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Settings</h2>
        <p className="text-sm text-gray-600">
          Configure your brand, preferences, and integrations
        </p>
      </div>

      {/* User Profile */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900 flex items-center">
            <UserIcon className="h-5 w-5 mr-2" />
            Profile
          </h3>
        </div>
        <div className="p-6">
          <div className="flex items-center space-x-4">
            <div className="h-16 w-16 bg-blue-100 rounded-full flex items-center justify-center">
              <UserIcon className="h-8 w-8 text-blue-600" />
            </div>
            <div>
              <h4 className="text-lg font-medium text-gray-900">
                {user?.name || 'Anonymous User'}
              </h4>
              <p className="text-sm text-gray-600">
                {user?.email || 'No email available'}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Member since {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'Unknown'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* System Status */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900 flex items-center">
            <CogIcon className="h-5 w-5 mr-2" />
            System Status
          </h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                {getStatusIcon(connectionStatus)}
                <div>
                  <p className="font-medium text-gray-900">API Connection</p>
                  <p className={`text-sm ${getStatusColor(connectionStatus)}`}>
                    {connectionStatus}
                  </p>
                </div>
              </div>
              <button
                onClick={checkApiHealth}
                className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200"
              >
                Test
              </button>
            </div>
            
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <CheckCircleIcon className="h-5 w-5 text-green-500" />
                <div>
                  <p className="font-medium text-gray-900">Database</p>
                  <p className="text-sm text-green-600">Connected</p>
                </div>
              </div>
              <span className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded-md">
                Healthy
              </span>
            </div>
          </div>
          
          {apiHealth && (
            <div className="mt-4 p-4 bg-blue-50 rounded-lg">
              <h4 className="font-medium text-blue-900 mb-2">API Health Details</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-blue-700">Version:</span>
                  <span className="ml-2 text-blue-900">{apiHealth.version || 'Unknown'}</span>
                </div>
                <div>
                  <span className="text-blue-700">Uptime:</span>
                  <span className="ml-2 text-blue-900">{apiHealth.uptime || 'Unknown'}</span>
                </div>
                <div>
                  <span className="text-blue-700">Memory:</span>
                  <span className="ml-2 text-blue-900">{apiHealth.memory_usage || 'Unknown'}</span>
                </div>
                <div>
                  <span className="text-blue-700">Load:</span>
                  <span className="ml-2 text-blue-900">{apiHealth.cpu_usage || 'Unknown'}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Notifications */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900 flex items-center">
            <BellIcon className="h-5 w-5 mr-2" />
            Notifications
          </h3>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {Object.entries(settings.notifications).map(([key, enabled]) => (
              <div key={key} className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900">
                    {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                  </p>
                  <p className="text-sm text-gray-600">
                    {key === 'goalMilestones' && 'Get notified when you reach goal milestones'}
                    {key === 'contentPublished' && 'Get notified when content is published'}
                    {key === 'workflowComplete' && 'Get notified when workflows complete'}
                    {key === 'systemAlerts' && 'Get notified about system issues'}
                    {key === 'apiErrors' && 'Get notified about API errors'}
                  </p>
                </div>
                <button
                  onClick={() => handleNotificationChange(key)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                    enabled ? 'bg-blue-600' : 'bg-gray-200'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      enabled ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
            ))}
          </div>
          
          <div className="mt-6 pt-6 border-t border-gray-200">
            <button
              onClick={handleTestNotification}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Test Notifications
            </button>
          </div>
        </div>
      </div>

      {/* Automation Settings */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900 flex items-center">
            <CogIcon className="h-5 w-5 mr-2" />
            Automation
          </h3>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {Object.entries(settings.automation).map(([key, enabled]) => (
              <div key={key} className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900">
                    {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                  </p>
                  <p className="text-sm text-gray-600">
                    {key === 'dailyWorkflows' && 'Automatically run daily content workflows'}
                    {key === 'autoOptimization' && 'Automatically optimize content based on performance'}
                    {key === 'smartScheduling' && 'Use AI to determine optimal posting times'}
                    {key === 'contentGeneration' && 'Enable automated content generation'}
                  </p>
                </div>
                <button
                  onClick={() => handleAutomationChange(key)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                    enabled ? 'bg-blue-600' : 'bg-gray-200'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      enabled ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Platform Integrations */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900 flex items-center">
            <LinkIcon className="h-5 w-5 mr-2" />
            Platform Integrations
          </h3>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {Object.entries(settings.platforms).map(([platform, config]) => (
              <div key={platform} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-bold ${
                    platform === 'twitter' ? 'bg-sky-500' :
                    platform === 'linkedin' ? 'bg-blue-600' :
                    platform === 'instagram' ? 'bg-pink-600' :
                    'bg-indigo-600'
                  }`}>
                    {platform.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 capitalize">{platform}</p>
                    <p className="text-sm text-gray-600">
                      {config.connected ? `Connected as @${config.username}` : 'Not connected'}
                    </p>
                  </div>
                </div>
                <button
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    config.connected
                      ? 'bg-red-100 text-red-700 hover:bg-red-200'
                      : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                  }`}
                >
                  {config.connected ? 'Disconnect' : 'Connect'}
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Advanced Settings */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900 flex items-center">
            <KeyIcon className="h-5 w-5 mr-2" />
            Advanced
          </h3>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-900">Clear Cache</p>
                <p className="text-sm text-gray-600">Clear all cached data to free up space</p>
              </div>
              <button
                onClick={handleClearCache}
                disabled={isLoading}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors disabled:opacity-50"
              >
                {isLoading ? 'Clearing...' : 'Clear Cache'}
              </button>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-900">Export Data</p>
                <p className="text-sm text-gray-600">Download all your data as JSON</p>
              </div>
              <button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors">
                Export
              </button>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-900">API Documentation</p>
                <p className="text-sm text-gray-600">View API documentation and examples</p>
              </div>
              <button className="px-4 py-2 bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors">
                View Docs
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}