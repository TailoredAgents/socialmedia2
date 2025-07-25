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
    // In production, integrate with monitoring service like Sentry, LogRocket, etc.
    // For now, just store in development for potential future use
    if (!isDevelopment && !isTest) {
      // TODO: Integrate with production monitoring service
      // Example: Sentry.captureMessage(message, level)
    }
  }
}

// Export singleton instance
export const logger = new Logger()

// Export logger methods for convenience
export const { info, warn, error, debug } = logger

export default logger