const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL
    this.token = null
  }

  setToken(token) {
    this.token = token
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    if (this.token) {
      config.headers.Authorization = `Bearer ${this.token}`
    }

    if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body)
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      }

      const contentType = response.headers.get('content-type')
      if (contentType && contentType.includes('application/json')) {
        return await response.json()
      }
      
      return await response.text()
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error)
      throw error
    }
  }

  // Auth endpoints
  async register(userData) {
    return this.request('/api/auth/register', {
      method: 'POST',
      body: userData
    })
  }

  async login(credentials) {
    return this.request('/api/auth/login', {
      method: 'POST',
      body: credentials
    })
  }

  async getCurrentUser() {
    return this.request('/api/auth/me')
  }

  async refreshToken() {
    return this.request('/api/auth/refresh', {
      method: 'POST'
    })
  }

  async logout() {
    return this.request('/api/auth/logout', {
      method: 'POST'
    })
  }

  async verifyAuth() {
    return this.request('/api/auth/verify')
  }

  async getAuthConfig() {
    return this.request('/api/auth/config')
  }

  // Memory endpoints (v2)
  async storeMemory(content, metadata) {
    return this.request('/api/memory/store', {
      method: 'POST',
      body: { content, metadata }
    })
  }

  async searchMemory(query, limit = 5) {
    return this.request('/api/memory/search', {
      method: 'POST',
      body: { query, limit }
    })
  }

  async getAllMemory(page = 1, limit = 20) {
    return this.request(`/api/memory/?page=${page}&limit=${limit}`)
  }

  async getMemoryById(contentId) {
    return this.request(`/api/memory/${contentId}`)
  }

  async updateMemory(contentId, data) {
    return this.request(`/api/memory/${contentId}`, {
      method: 'PUT',
      body: data
    })
  }

  async deleteMemory(contentId) {
    return this.request(`/api/memory/${contentId}`, {
      method: 'DELETE'
    })
  }

  async getMemoryAnalytics() {
    return this.request('/api/memory/analytics/summary')
  }

  async getPopularTags() {
    return this.request('/api/memory/tags/popular')
  }

  // Vector Memory endpoints
  async storeVector(content, embedding, metadata) {
    return this.request('/api/memory/vector/store', {
      method: 'POST',
      body: { content, embedding, metadata }
    })
  }

  async searchVector(query, limit = 5, threshold = 0.8) {
    return this.request('/api/memory/vector/search', {
      method: 'POST',
      body: { query, limit, threshold }
    })
  }

  async getHighPerformingContent() {
    return this.request('/api/memory/vector/high-performing')
  }

  async getRepurposingCandidates() {
    return this.request('/api/memory/vector/repurposing-candidates')
  }

  async analyzeContentPatterns() {
    return this.request('/api/memory/vector/patterns')
  }

  async getVectorStats() {
    return this.request('/api/memory/vector/stats')
  }

  async syncVectorStore() {
    return this.request('/api/memory/vector/sync', {
      method: 'POST'
    })
  }

  async getContentByType(memoryType) {
    return this.request(`/api/memory/vector/by-type/${memoryType}`)
  }

  // Goals endpoints (v2)
  async createGoal(goalData) {
    return this.request('/api/goals/', {
      method: 'POST',
      body: goalData
    })
  }

  async getGoals() {
    return this.request('/api/goals/')
  }

  async getGoal(goalId) {
    return this.request(`/api/goals/${goalId}`)
  }

  async updateGoal(goalId, goalData) {
    return this.request(`/api/goals/${goalId}`, {
      method: 'PUT',
      body: goalData
    })
  }

  async updateGoalProgress(goalId, progressData) {
    return this.request(`/api/goals/${goalId}/progress`, {
      method: 'PUT',
      body: progressData
    })
  }

  async pauseGoal(goalId) {
    return this.request(`/api/goals/${goalId}/pause`, {
      method: 'PUT'
    })
  }

  async resumeGoal(goalId) {
    return this.request(`/api/goals/${goalId}/resume`, {
      method: 'PUT'
    })
  }

  async deleteGoal(goalId) {
    return this.request(`/api/goals/${goalId}`, {
      method: 'DELETE'
    })
  }

  async getGoalProgress(goalId) {
    return this.request(`/api/goals/${goalId}/progress`)
  }

  async getGoalsDashboard() {
    return this.request('/api/goals/dashboard/summary')
  }

  // Analytics endpoints (using main.py endpoints)
  async getMetrics() {
    return this.request('/api/metrics')
  }

  async getAnalytics(timeframe = '7d') {
    return this.request(`/api/analytics?timeframe=${timeframe}`)
  }

  async getPerformanceMetrics(platform = 'all') {
    return this.request(`/api/analytics/performance?platform=${platform}`)
  }

  // Content endpoints
  async createContent(contentData) {
    return this.request('/api/content/', {
      method: 'POST',
      body: contentData
    })
  }

  async getContent(page = 1, limit = 20) {
    return this.request(`/api/content/?page=${page}&limit=${limit}`)
  }

  async getContentById(contentId) {
    return this.request(`/api/content/${contentId}`)
  }

  async updateContent(contentId, contentData) {
    return this.request(`/api/content/${contentId}`, {
      method: 'PUT',
      body: contentData
    })
  }

  async publishContent(contentId) {
    return this.request(`/api/content/${contentId}/publish`, {
      method: 'POST'
    })
  }

  async scheduleContent(contentId, scheduleData) {
    return this.request(`/api/content/${contentId}/schedule`, {
      method: 'POST',
      body: scheduleData
    })
  }

  async deleteContent(contentId) {
    return this.request(`/api/content/${contentId}`, {
      method: 'DELETE'
    })
  }

  async getUpcomingContent() {
    return this.request('/api/content/scheduled/upcoming')
  }

  async getContentAnalytics() {
    return this.request('/api/content/analytics/summary')
  }

  async generateContent(prompt, contentType) {
    return this.request('/api/content/generate', {
      method: 'POST',
      body: { prompt, content_type: contentType }
    })
  }

  // Workflow endpoints (v2)
  async executeWorkflow(workflowData) {
    return this.request('/api/workflow/execute', {
      method: 'POST',
      body: workflowData
    })
  }

  async getWorkflowExecutions() {
    return this.request('/api/workflow/')
  }

  async getWorkflowExecution(executionId) {
    return this.request(`/api/workflow/${executionId}`)
  }

  async cancelWorkflowExecution(executionId) {
    return this.request(`/api/workflow/${executionId}/cancel`, {
      method: 'POST'
    })
  }

  async getWorkflowStatusSummary() {
    return this.request('/api/workflow/status/summary')
  }

  async executeDailyWorkflow() {
    return this.request('/api/workflow/templates/daily', {
      method: 'POST'
    })
  }

  async executeOptimizationWorkflow() {
    return this.request('/api/workflow/templates/optimization', {
      method: 'POST'
    })
  }

  // Legacy workflow endpoints (main.py)
  async getWorkflowStatus() {
    return this.request('/api/workflow/status')
  }

  async triggerWorkflow(workflowType) {
    return this.request('/api/workflow/trigger', {
      method: 'POST',
      body: { workflow_type: workflowType }
    })
  }

  // Notifications endpoints
  async getNotifications() {
    return this.request('/api/notifications/')
  }

  async getNotificationsSummary() {
    return this.request('/api/notifications/summary')
  }

  async markNotificationRead(notificationId) {
    return this.request(`/api/notifications/${notificationId}/read`, {
      method: 'PUT'
    })
  }

  async dismissNotification(notificationId) {
    return this.request(`/api/notifications/${notificationId}/dismiss`, {
      method: 'PUT'
    })
  }

  async markAllNotificationsRead() {
    return this.request('/api/notifications/mark-all-read', {
      method: 'PUT'
    })
  }

  async deleteNotification(notificationId) {
    return this.request(`/api/notifications/${notificationId}`, {
      method: 'DELETE'
    })
  }

  async checkGoalNotifications() {
    return this.request('/api/notifications/check-goals', {
      method: 'POST'
    })
  }

  async getNotificationTypes() {
    return this.request('/api/notifications/types')
  }

  // Health and system endpoints
  async getHealth() {
    return this.request('/api/health')
  }

  async getAuthStatus() {
    return this.request('/api/auth/status')
  }

  async getMemoryStats() {
    return this.request('/api/memory/stats')
  }

  async getGoalsSummary() {
    return this.request('/api/goals/summary')
  }
}

// Create singleton instance
const apiService = new ApiService()

export default apiService