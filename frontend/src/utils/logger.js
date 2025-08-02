// Production-ready logging utility
// Only logs in development mode, sends to monitoring service in production

const isDevelopment = import.meta.env.MODE === 'development'
const isTest = import.meta.env.MODE === 'test'

class Logger {
  constructor() {
    this.isEnabled = isDevelopment && !isTest
  }

  info(message, ...args) {
    if (this.isEnabled) {
      console.log(`[INFO] ${message}`, ...args)
    }
    // In production, could send to monitoring service
    this._sendToMonitoring('info', message, args)
  }

  warn(message, ...args) {
    if (this.isEnabled) {
      console.warn(`[WARN] ${message}`, ...args)
    }
    this._sendToMonitoring('warn', message, args)
  }

  error(message, error, ...args) {
    if (this.isEnabled) {
      console.error(`[ERROR] ${message}`, error, ...args)
    }
    // Always log errors for monitoring in production
    this._sendToMonitoring('error', message, { error, args })
  }

  debug(message, ...args) {
    if (this.isEnabled) {
      console.log(`[DEBUG] ${message}`, ...args)
    }
    // Debug logs only in development
  }

  _sendToMonitoring(level, message, data) {
    // Temporarily disabled to prevent 404 spam
    // TODO: Implement proper monitoring endpoint in backend
    return
  }

  _mapLevelToSentryLevel(level) {
    const levelMap = {
      'error': 'error',
      'warn': 'warning', 
      'info': 'info',
      'debug': 'debug'
    }
    return levelMap[level] || 'info'
  }

  _sendToCustomEndpoint(level, message, data) {
    // Temporarily disabled - no logging endpoint available
    return
  }

  _getSessionId() {
    // Simple session ID generation for tracking
    if (typeof window !== 'undefined') {
      let sessionId = sessionStorage.getItem('logger-session-id')
      if (!sessionId) {
        sessionId = Date.now().toString(36) + Math.random().toString(36).substr(2)
        sessionStorage.setItem('logger-session-id', sessionId)
      }
      return sessionId
    }
    return 'unknown'
  }
}

// Export singleton instance
export const logger = new Logger()

// Export logger methods for convenience - defensive destructuring
export const info = (...args) => logger?.info?.(...args) || console.log(...args)
export const warn = (...args) => logger?.warn?.(...args) || console.warn(...args)
export const error = (...args) => logger?.error?.(...args) || console.error(...args)
export const debug = (...args) => logger?.debug?.(...args) || console.log(...args)

export default logger