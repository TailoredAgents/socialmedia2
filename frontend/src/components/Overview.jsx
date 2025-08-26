import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Line, Doughnut, Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

// Empty state data - replace with API calls
const emptyMetrics = {
  totalPosts: 0,
  engagement: 0,
  followers: 0,
  roi: 0,
  postsGrowth: 0,
  engagementGrowth: 0,
  followersGrowth: 0,
  roiGrowth: 0
}

const emptyChartData = {
  followerGrowth: {
    labels: [],
    datasets: [{
      label: 'Followers',
      data: [],
      borderColor: '#008080',
      backgroundColor: 'rgba(0, 128, 128, 0.1)',
      fill: true,
      tension: 0.4
    }]
  },
  engagementBreakdown: {
    labels: [],
    datasets: [{
      data: [],
      backgroundColor: ['#008080', '#FFD700', '#20B2AA', '#87CEEB'],
      borderWidth: 0
    }]
  },
  contentPerformance: {
    labels: [],
    datasets: [{
      label: 'Engagement Rate',
      data: [],
      backgroundColor: 'rgba(0, 128, 128, 0.8)',
      borderRadius: 8
    }]
  }
}

// Metric Card Component
const MetricCard = ({ title, value, growth, icon, darkMode, delay = 0 }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.6, delay }}
    className={`p-6 rounded-xl backdrop-blur-md ${
      darkMode ? 'bg-gray-800/80' : 'bg-white/80'
    } border border-gray-200/20 shadow-lg`}
  >
    <div className="flex items-center justify-between">
      <div>
        <p className={`text-sm font-medium ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
          {title}
        </p>
        <p className={`text-2xl font-bold mt-2 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
          {value}
        </p>
        <p className={`text-sm mt-1 ${growth >= 0 ? 'text-green-500' : 'text-red-500'}`}>
          {growth >= 0 ? '↗️' : '↘️'} {Math.abs(growth)}% this month
        </p>
      </div>
      <div className="text-3xl">
        {icon}
      </div>
    </div>
  </motion.div>
)

// Chart Container Component
const ChartContainer = ({ title, children, darkMode, delay = 0 }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.6, delay }}
    className={`p-6 rounded-xl backdrop-blur-md ${
      darkMode ? 'bg-gray-800/80' : 'bg-white/80'
    } border border-gray-200/20 shadow-lg`}
  >
    <h3 className={`text-lg font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
      {title}
    </h3>
    {children}
  </motion.div>
)

// Recent Activity Component
const RecentActivity = ({ darkMode }) => {
  const activities = [
    { id: 1, type: 'post', content: 'Published "AI in Marketing 2025"', time: '2 hours ago', status: 'success' },
    { id: 2, type: 'analytics', content: 'Generated weekly report', time: '4 hours ago', status: 'info' },
    { id: 3, type: 'alert', content: 'High engagement on LinkedIn post', time: '6 hours ago', status: 'warning' },
    { id: 4, type: 'research', content: 'Completed trend analysis', time: '8 hours ago', status: 'success' }
  ]

  const getStatusColor = (status) => {
    switch (status) {
      case 'success': return 'text-green-500'
      case 'warning': return 'text-yellow-500'
      case 'info': return 'text-blue-500'
      default: return 'text-gray-500'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success': return '✅'
      case 'warning': return '⚠️'
      case 'info': return 'ℹ️'
      default: return '📝'
    }
  }

  return (
    <div className={`p-6 rounded-xl backdrop-blur-md ${
      darkMode ? 'bg-gray-800/80' : 'bg-white/80'
    } border border-gray-200/20 shadow-lg`}>
      <h3 className={`text-lg font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
        Recent Activity
      </h3>
      <div className="space-y-4">
        {activities.map((activity, index) => (
          <motion.div
            key={activity.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4, delay: index * 0.1 }}
            className="flex items-center space-x-3"
          >
            <span className={`text-lg ${getStatusColor(activity.status)}`}>
              {getStatusIcon(activity.status)}
            </span>
            <div className="flex-1">
              <p className={`text-sm font-medium ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                {activity.content}
              </p>
              <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                {activity.time}
              </p>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

// AI Status Component
const AIStatus = ({ darkMode }) => {
  const [status, setStatus] = useState('active')
  const [currentTask, setCurrentTask] = useState('Content Generation')

  useEffect(() => {
    const tasks = ['Content Generation', 'Trend Analysis', 'Engagement Optimization', 'Research']
    const interval = setInterval(() => {
      setCurrentTask(tasks[Math.floor(Math.random() * tasks.length)])
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className={`p-6 rounded-xl backdrop-blur-md ${
      darkMode ? 'bg-gray-800/80' : 'bg-white/80'
    } border border-gray-200/20 shadow-lg`}>
      <h3 className={`text-lg font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
        AI Agent Status
      </h3>
      
      <div className="flex items-center space-x-3 mb-4">
        <motion.div
          className="w-3 h-3 bg-green-500 rounded-full"
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
        />
        <span className={`font-medium ${darkMode ? 'text-white' : 'text-gray-900'}`}>
          Active & Running
        </span>
      </div>

      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <span className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
            Current Task:
          </span>
          <motion.span
            key={currentTask}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className={`text-sm font-medium ${darkMode ? 'text-white' : 'text-gray-900'}`}
          >
            {currentTask}
          </motion.span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
            Tasks Completed:
          </span>
          <span className={`text-sm font-medium text-green-500`}>
            247 today
          </span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
            Efficiency:
          </span>
          <span className={`text-sm font-medium text-blue-500`}>
            96.8%
          </span>
        </div>
      </div>
    </div>
  )
}

// Today's Plan Action Strip Component
const TodaysPlan = ({ darkMode, autopilotMode }) => {
  const [currentTime] = useState(new Date())
  
  // Generate context-aware suggestions based on time and autopilot mode
  const getContextualSuggestions = () => {
    const hour = currentTime.getHours()
    const dayOfWeek = currentTime.getDay() // 0 = Sunday, 1 = Monday, etc.
    
    const suggestions = []
    
    // Time-based suggestions
    if (hour >= 9 && hour <= 11) {
      suggestions.push({
        id: 'morning_content',
        title: 'Create Morning Content',
        description: 'Perfect time for thought leadership posts',
        action: 'Create Post',
        icon: '☀️',
        priority: 'high',
        timeEstimate: '10 min'
      })
    } else if (hour >= 12 && hour <= 14) {
      suggestions.push({
        id: 'lunch_engagement',
        title: 'Engage with Community',
        description: 'Peak engagement hours - reply to comments',
        action: 'Review Inbox',
        icon: '💬',
        priority: 'medium',
        timeEstimate: '15 min'
      })
    } else if (hour >= 15 && hour <= 17) {
      suggestions.push({
        id: 'afternoon_schedule',
        title: 'Schedule Tomorrow\'s Content',
        description: 'Plan and queue up tomorrow\'s posts',
        action: 'Open Scheduler',
        icon: '📅',
        priority: 'high',
        timeEstimate: '12 min'
      })
    } else if (hour >= 18 && hour <= 20) {
      suggestions.push({
        id: 'evening_analytics',
        title: 'Review Today\'s Performance',
        description: 'Check analytics and optimize strategy',
        action: 'View Analytics',
        icon: '📊',
        priority: 'medium',
        timeEstimate: '8 min'
      })
    }
    
    // Autopilot mode specific suggestions
    if (autopilotMode) {
      suggestions.push({
        id: 'autopilot_review',
        title: 'Review Autopilot Actions',
        description: 'Check what Lily accomplished automatically today',
        action: 'View Report',
        icon: '🚁',
        priority: 'low',
        timeEstimate: '5 min'
      })
    } else {
      suggestions.push({
        id: 'pending_approvals',
        title: 'Pending Approvals',
        description: 'Lily has 3 drafts waiting for your review',
        action: 'Review Drafts',
        icon: '👀',
        priority: 'high',
        timeEstimate: '7 min'
      })
    }
    
    // Day-of-week specific suggestions
    if (dayOfWeek === 1) { // Monday
      suggestions.push({
        id: 'week_planning',
        title: 'Plan This Week',
        description: 'Set content themes and goals for the week',
        action: 'Plan Week',
        icon: '🗓️',
        priority: 'high',
        timeEstimate: '20 min'
      })
    } else if (dayOfWeek === 5) { // Friday
      suggestions.push({
        id: 'week_review',
        title: 'Weekly Review',
        description: 'Analyze this week\'s performance and insights',
        action: 'View Report',
        icon: '📈',
        priority: 'medium',
        timeEstimate: '15 min'
      })
    }
    
    // Always include content research
    suggestions.push({
      id: 'research_trends',
      title: 'Research Trending Topics',
      description: 'Find fresh content ideas from industry trends',
      action: 'Research Topics',
      icon: '🔍',
      priority: 'medium',
      timeEstimate: '10 min'
    })
    
    return suggestions.sort((a, b) => {
      const priorityOrder = { high: 3, medium: 2, low: 1 }
      return priorityOrder[b.priority] - priorityOrder[a.priority]
    }).slice(0, 4) // Show top 4 suggestions
  }
  
  const suggestions = getContextualSuggestions()
  
  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return darkMode ? 'border-red-400 bg-red-900/20' : 'border-red-300 bg-red-50'
      case 'medium': return darkMode ? 'border-yellow-400 bg-yellow-900/20' : 'border-yellow-300 bg-yellow-50'
      case 'low': return darkMode ? 'border-blue-400 bg-blue-900/20' : 'border-blue-300 bg-blue-50'
      default: return darkMode ? 'border-gray-400 bg-gray-900/20' : 'border-gray-300 bg-gray-50'
    }
  }
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.2 }}
      className={`p-6 rounded-xl backdrop-blur-md ${
        darkMode ? 'bg-gray-800/80' : 'bg-white/80'
      } border border-gray-200/20 shadow-lg`}
    >
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
            Today's Action Plan
          </h3>
          <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
            Smart suggestions based on optimal timing and your current setup
          </p>
        </div>
        <div className="flex items-center space-x-2 text-sm">
          <span className={`${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
            {currentTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
          <div className={`w-2 h-2 rounded-full ${autopilotMode ? 'bg-green-400' : 'bg-blue-400'} animate-pulse`} />
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {suggestions.map((suggestion, index) => (
          <motion.div
            key={suggestion.id}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, delay: 0.1 * index }}
            className={`p-4 rounded-lg border-2 ${getPriorityColor(suggestion.priority)} hover:shadow-md transition-all cursor-pointer group`}
          >
            <div className="flex items-start justify-between mb-2">
              <span className="text-2xl">{suggestion.icon}</span>
              <span className={`text-xs px-2 py-1 rounded-full ${
                suggestion.priority === 'high' 
                  ? 'bg-red-100 text-red-700' 
                  : suggestion.priority === 'medium'
                  ? 'bg-yellow-100 text-yellow-700'
                  : 'bg-blue-100 text-blue-700'
              }`}>
                {suggestion.timeEstimate}
              </span>
            </div>
            <h4 className={`font-medium mb-1 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
              {suggestion.title}
            </h4>
            <p className={`text-xs mb-3 ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
              {suggestion.description}
            </p>
            <button className={`w-full px-3 py-2 text-sm font-medium rounded-md transition-colors ${
              darkMode 
                ? 'bg-blue-600 text-white hover:bg-blue-500' 
                : 'bg-blue-500 text-white hover:bg-blue-600'
            } group-hover:shadow-sm`}>
              {suggestion.action}
            </button>
          </motion.div>
        ))}
      </div>
      
      <div className={`mt-4 pt-4 border-t ${darkMode ? 'border-gray-700' : 'border-gray-200'} flex items-center justify-between`}>
        <p className={`text-xs ${darkMode ? 'text-gray-500' : 'text-gray-500'}`}>
          💡 Suggestions refresh automatically based on time and your activity patterns
        </p>
        <button className={`text-xs ${darkMode ? 'text-blue-400 hover:text-blue-300' : 'text-blue-600 hover:text-blue-500'} transition-colors`}>
          Refresh Suggestions
        </button>
      </div>
    </motion.div>
  )
}

// Setup Progress Component
const SetupProgress = ({ darkMode }) => {
  const setupProgress = calculateSetupProgress()
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className={`p-6 rounded-xl backdrop-blur-md ${
        darkMode ? 'bg-gray-800/80' : 'bg-white/80'
      } border border-gray-200/20 shadow-lg`}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
          Setup Progress
        </h3>
        <span className={`text-sm font-medium px-3 py-1 rounded-full ${
          setupProgress.percentage === 100 
            ? 'bg-green-100 text-green-800' 
            : 'bg-blue-100 text-blue-800'
        }`}>
          {setupProgress.completed}/{setupProgress.total} Complete
        </span>
      </div>
      
      {/* Progress Bar */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
            Overall Progress
          </span>
          <span className={`text-sm font-medium ${darkMode ? 'text-white' : 'text-gray-900'}`}>
            {setupProgress.percentage}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <motion.div
            className="bg-gradient-to-r from-teal-500 to-blue-500 h-2 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${setupProgress.percentage}%` }}
            transition={{ duration: 1, delay: 0.3 }}
          />
        </div>
      </div>
      
      {/* Next Step */}
      {setupProgress.nextStep && (
        <div className={`p-3 rounded-lg ${darkMode ? 'bg-gray-700/50' : 'bg-blue-50'} border-l-4 border-blue-500`}>
          <div className="flex items-center justify-between">
            <div>
              <p className={`font-medium ${darkMode ? 'text-white' : 'text-blue-900'}`}>
                Next Step: {setupProgress.nextStep.name}
              </p>
              <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-blue-700'}`}>
                {setupProgress.nextStep.description}
              </p>
            </div>
            <button className="px-3 py-1 bg-blue-500 text-white text-sm rounded-md hover:bg-blue-600 transition-colors">
              Setup
            </button>
          </div>
        </div>
      )}
      
      {setupProgress.percentage === 100 && (
        <div className={`p-3 rounded-lg ${darkMode ? 'bg-green-900/20' : 'bg-green-50'} border-l-4 border-green-500`}>
          <p className={`font-medium ${darkMode ? 'text-green-400' : 'text-green-900'}`}>
            🎉 Setup Complete!
          </p>
          <p className={`text-sm ${darkMode ? 'text-green-300' : 'text-green-700'}`}>
            Your AI social media agent is fully configured and ready to fly on autopilot.
          </p>
        </div>
      )}
    </motion.div>
  )
}

// Calculate outcome metrics
const calculateOutcomeMetrics = () => {
  // For now, use estimated/projected values since we're in empty state
  const postsCreatedThisWeek = 8 // Could come from API later
  const postsScheduledNext7Days = 12
  const commentsHandledThisWeek = 23
  const lastWeekEngagement = 156
  const thisWeekEngagement = 189
  
  return {
    hoursSaved: Math.round((postsCreatedThisWeek * 12 + commentsHandledThisWeek * 0.75) / 60 * 10) / 10, // 12 min per post, 45s per comment
    leadsCaptured: 3, // From escalated comments/DMs
    consistencyScore: Math.round((postsScheduledNext7Days / 7) * 100),
    engagementLift: Math.round(((thisWeekEngagement - lastWeekEngagement) / lastWeekEngagement) * 100)
  }
}

// Calculate setup completion progress
const calculateSetupProgress = () => {
  const setupSteps = [
    { id: 'company_info', name: 'Company Information', completed: true, description: 'Basic company details configured' },
    { id: 'brand_voice', name: 'Brand Voice & Tone', completed: true, description: 'Brand personality settings defined' },
    { id: 'social_platforms', name: 'Social Platform Connections', completed: false, description: 'Connect Twitter, LinkedIn, Instagram' },
    { id: 'content_categories', name: 'Content Categories', completed: true, description: 'Define content themes and topics' },
    { id: 'automation_rules', name: 'Automation Preferences', completed: false, description: 'Configure posting schedules and rules' },
    { id: 'first_post', name: 'First AI-Generated Post', completed: true, description: 'Create and publish your first post' }
  ]
  
  const completedSteps = setupSteps.filter(step => step.completed).length
  const progressPercentage = Math.round((completedSteps / setupSteps.length) * 100)
  
  return {
    steps: setupSteps,
    completed: completedSteps,
    total: setupSteps.length,
    percentage: progressPercentage,
    nextStep: setupSteps.find(step => !step.completed)
  }
}

// Main Overview Component
const Overview = ({ darkMode, searchQuery }) => {
  const [autopilotMode, setAutopilotMode] = useState(false)
  const outcomeMetrics = calculateOutcomeMetrics()
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        backgroundColor: darkMode ? '#374151' : '#ffffff',
        titleColor: darkMode ? '#ffffff' : '#000000',
        bodyColor: darkMode ? '#ffffff' : '#000000',
        borderColor: darkMode ? '#6b7280' : '#e5e7eb',
        borderWidth: 1
      }
    },
    scales: {
      x: {
        grid: {
          color: darkMode ? '#374151' : '#f3f4f6'
        },
        ticks: {
          color: darkMode ? '#9ca3af' : '#6b7280'
        }
      },
      y: {
        grid: {
          color: darkMode ? '#374151' : '#f3f4f6'
        },
        ticks: {
          color: darkMode ? '#9ca3af' : '#6b7280'
        }
      }
    }
  }

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: darkMode ? '#ffffff' : '#000000',
          usePointStyle: true,
          padding: 20
        }
      },
      tooltip: {
        backgroundColor: darkMode ? '#374151' : '#ffffff',
        titleColor: darkMode ? '#ffffff' : '#000000',
        bodyColor: darkMode ? '#ffffff' : '#000000',
        borderColor: darkMode ? '#6b7280' : '#e5e7eb',
        borderWidth: 1
      }
    }
  }

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className={`p-8 rounded-xl bg-gradient-to-r from-teal-600 to-blue-600 text-white`}
      >
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-4 mb-3">
              <h1 className="text-3xl font-bold">
                Flight Deck - Social Media Autopilot
              </h1>
              
              {/* Autopilot Toggle */}
              <div className="flex items-center space-x-3 bg-white/20 backdrop-blur-md rounded-full px-4 py-2">
                <span className="text-sm font-medium">Review Mode</span>
                <button
                  onClick={() => setAutopilotMode(!autopilotMode)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-teal-600 ${
                    autopilotMode ? 'bg-green-500' : 'bg-gray-400'
                  }`}
                >
                  <motion.span
                    className="inline-block h-4 w-4 transform rounded-full bg-white shadow-lg"
                    animate={{ x: autopilotMode ? 24 : 4 }}
                    transition={{ type: "spring", stiffness: 500, damping: 30 }}
                  />
                </button>
                <span className="text-sm font-medium">Full Autopilot</span>
              </div>
            </div>
            
            <p className="text-teal-100 text-lg mb-1">
              Your social on autopilot—research → draft → schedule → reply
            </p>
            <p className="text-teal-200 text-sm mb-4">
              {autopilotMode 
                ? "🚁 Full Autopilot: Lily posts and replies automatically without asking for approval" 
                : "👀 Review Mode: Lily drafts content and asks for your approval before posting"
              }
            </p>
            
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-2">
                <span className="text-2xl">✈️</span>
                <span>{autopilotMode ? 'Full Autopilot Active' : 'Autopilot Ready'}</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-2xl">⏱️</span>
                <span>7.2 hours saved this week</span>
              </div>
            </div>
          </div>
          <div className="text-6xl opacity-20">
            {autopilotMode ? '🚁' : '🤖'}
          </div>
        </div>
      </motion.div>

      {/* Today's Action Plan */}
      <TodaysPlan darkMode={darkMode} autopilotMode={autopilotMode} />

      {/* Outcome Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Hours Saved"
          value={`${outcomeMetrics.hoursSaved}h`}
          growth={22.3}
          icon="⏱️"
          darkMode={darkMode}
          delay={0.1}
        />
        <MetricCard
          title="Leads Captured"
          value={outcomeMetrics.leadsCaptured}
          growth={outcomeMetrics.leadsCaptured > 0 ? 100 : 0}
          icon="🎯"
          darkMode={darkMode}
          delay={0.2}
        />
        <MetricCard
          title="Consistency Score"
          value={`${outcomeMetrics.consistencyScore}%`}
          growth={outcomeMetrics.consistencyScore > 85 ? 12.4 : -8.2}
          icon="📅"
          darkMode={darkMode}
          delay={0.3}
        />
        <MetricCard
          title="Engagement Lift"
          value={`${outcomeMetrics.engagementLift > 0 ? '+' : ''}${outcomeMetrics.engagementLift}%`}
          growth={outcomeMetrics.engagementLift}
          icon="📈"
          darkMode={darkMode}
          delay={0.4}
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartContainer title="Follower Growth" darkMode={darkMode} delay={0.5}>
          <div className="h-64">
            <Line data={emptyChartData.followerGrowth} options={chartOptions} />
          </div>
        </ChartContainer>

        <ChartContainer title="Engagement Breakdown" darkMode={darkMode} delay={0.6}>
          <div className="h-64">
            <Doughnut data={emptyChartData.engagementBreakdown} options={doughnutOptions} />
          </div>
        </ChartContainer>
      </div>

      {/* Setup Progress */}
      <SetupProgress darkMode={darkMode} />

      {/* Content Performance & Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <ChartContainer title="Weekly Performance" darkMode={darkMode} delay={0.7}>
          <div className="h-48">
            <Bar data={emptyChartData.contentPerformance} options={chartOptions} />
          </div>
        </ChartContainer>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
        >
          <RecentActivity darkMode={darkMode} />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.9 }}
        >
          <AIStatus darkMode={darkMode} />
        </motion.div>
      </div>
    </div>
  )
}

export default Overview