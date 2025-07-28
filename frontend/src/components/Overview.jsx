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

// Mock data for demonstration
const mockMetrics = {
  totalPosts: 156,
  engagement: 4.2,
  followers: 2750,
  roi: 12500,
  postsGrowth: 12,
  engagementGrowth: 0.8,
  followersGrowth: 342,
  roiGrowth: 1800
}

const mockChartData = {
  followerGrowth: {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [{
      label: 'Followers',
      data: [2100, 2200, 2350, 2400, 2600, 2750],
      borderColor: '#008080',
      backgroundColor: 'rgba(0, 128, 128, 0.1)',
      fill: true,
      tension: 0.4
    }]
  },
  engagementBreakdown: {
    labels: ['Likes', 'Comments', 'Shares', 'Saves'],
    datasets: [{
      data: [45, 25, 20, 10],
      backgroundColor: ['#008080', '#FFD700', '#20B2AA', '#87CEEB'],
      borderWidth: 0
    }]
  },
  contentPerformance: {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [{
      label: 'Engagement Rate',
      data: [3.2, 4.1, 3.8, 4.5, 4.9, 3.6, 2.8],
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

// Main Overview Component
const Overview = ({ darkMode, searchQuery }) => {
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
            <h1 className="text-3xl font-bold mb-2">
              Welcome to Tailored Agents Dashboard
            </h1>
            <p className="text-teal-100 text-lg">
              Your AI is working 24/7 to grow your social media presence
            </p>
            <div className="mt-4 flex items-center space-x-6">
              <div className="flex items-center space-x-2">
                <span className="text-2xl">🚀</span>
                <span>156 posts this month</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-2xl">💰</span>
                <span>Saved $12,500 in time</span>
              </div>
            </div>
          </div>
          <div className="text-6xl opacity-20">
            🤖
          </div>
        </div>
      </motion.div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Posts"
          value={mockMetrics.totalPosts}
          growth={mockMetrics.postsGrowth}
          icon="📝"
          darkMode={darkMode}
          delay={0.1}
        />
        <MetricCard
          title="Engagement Rate"
          value={`${mockMetrics.engagement}%`}
          growth={mockMetrics.engagementGrowth}
          icon="💙"
          darkMode={darkMode}
          delay={0.2}
        />
        <MetricCard
          title="Followers"
          value={mockMetrics.followers.toLocaleString()}
          growth={15.2}
          icon="👥"
          darkMode={darkMode}
          delay={0.3}
        />
        <MetricCard
          title="Time Saved"
          value={`$${mockMetrics.roi.toLocaleString()}`}
          growth={18.5}
          icon="💰"
          darkMode={darkMode}
          delay={0.4}
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartContainer title="Follower Growth" darkMode={darkMode} delay={0.5}>
          <div className="h-64">
            <Line data={mockChartData.followerGrowth} options={chartOptions} />
          </div>
        </ChartContainer>

        <ChartContainer title="Engagement Breakdown" darkMode={darkMode} delay={0.6}>
          <div className="h-64">
            <Doughnut data={mockChartData.engagementBreakdown} options={doughnutOptions} />
          </div>
        </ChartContainer>
      </div>

      {/* Content Performance & Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <ChartContainer title="Weekly Performance" darkMode={darkMode} delay={0.7}>
          <div className="h-48">
            <Bar data={mockChartData.contentPerformance} options={chartOptions} />
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