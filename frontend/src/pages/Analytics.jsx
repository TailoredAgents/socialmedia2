import { useState, useEffect } from 'react'
import { 
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js'
import { Line, Bar, Doughnut } from 'react-chartjs-2'
import { 
  ArrowUpIcon, 
  ArrowDownIcon,
  EyeIcon,
  HeartIcon,
  ChatBubbleLeftIcon,
  ShareIcon,
  CalendarDaysIcon,
  FunnelIcon,
  BoltIcon
} from '@heroicons/react/24/outline'
import RealTimeMetrics from '../components/Analytics/RealTimeMetrics'
import { useApi } from '../hooks/useApi'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
)

// Mock analytics data
const mockAnalytics = {
  overview: {
    totalViews: 125000,
    totalEngagement: 8500,
    totalFollowers: 15200,
    engagementRate: 6.8,
    viewsChange: 12.5,
    engagementChange: -2.3,
    followersChange: 8.2,
    engagementRateChange: 1.4
  },
  timeRange: '7d',
  platforms: {
    twitter: { name: 'Twitter', followers: 5200, engagement: 3200, color: '#1DA1F2' },
    linkedin: { name: 'LinkedIn', followers: 3800, engagement: 2800, color: '#0077B5' },
    instagram: { name: 'Instagram', followers: 4200, engagement: 1800, color: '#E4405F' },
    facebook: { name: 'Facebook', followers: 2000, engagement: 700, color: '#1877F2' }
  },
  engagementTrend: {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'Engagement Rate',
        data: [6.2, 7.1, 5.8, 8.2, 6.9, 7.5, 6.8],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4,
      }
    ]
  },
  contentPerformance: {
    labels: ['Text Posts', 'Images', 'Videos', 'Carousels', 'Stories'],
    datasets: [
      {
        label: 'Avg Engagement',
        data: [245, 380, 520, 410, 180],
        backgroundColor: [
          'rgba(59, 130, 246, 0.8)',
          'rgba(16, 185, 129, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(139, 92, 246, 0.8)',
          'rgba(239, 68, 68, 0.8)',
        ],
        borderWidth: 0,
      }
    ]
  },
  topContent: [
    {
      id: 1,
      title: "5 AI Tools That Will Transform Your Social Media Strategy",
      platform: "linkedin",
      type: "text",
      views: 15200,
      likes: 340,
      comments: 28,
      shares: 45,
      engagement_rate: 2.7,
      posted_at: "2025-07-20"
    },
    {
      id: 2,
      title: "Behind the scenes of our content creation process",
      platform: "instagram",
      type: "video",
      views: 8900,
      likes: 520,
      comments: 67,
      shares: 32,
      engagement_rate: 6.9,
      posted_at: "2025-07-19"
    },
    {
      id: 3,
      title: "Quick tips for better engagement on social media",
      platform: "twitter",
      type: "image",
      views: 4200,
      likes: 180,
      comments: 23,
      shares: 45,
      engagement_rate: 5.9,
      posted_at: "2025-07-18"
    }
  ]
}

const timeRanges = [
  { value: '7d', label: 'Last 7 days' },
  { value: '30d', label: 'Last 30 days' },
  { value: '90d', label: 'Last 3 months' },
  { value: '1y', label: 'Last year' }
]

export default function Analytics() {
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d')
  const [selectedPlatform, setSelectedPlatform] = useState('all')
  const [showRealTime, setShowRealTime] = useState(true)
  const [analyticsData, setAnalyticsData] = useState(mockAnalytics)
  const [isLoading, setIsLoading] = useState(false)
  
  const { apiService, makeAuthenticatedRequest } = useApi()

  // Load analytics data when timerange or platform changes
  useEffect(() => {
    const loadAnalytics = async () => {
      if (showRealTime) return // Real-time data is handled by RealTimeMetrics component
      
      try {
        setIsLoading(true)
        const metrics = await makeAuthenticatedRequest(apiService.getMetrics)
        
        // Transform backend data to match the expected format
        if (metrics) {
          setAnalyticsData(prevData => ({
            ...prevData,
            overview: {
              totalViews: metrics.total_views || 0,
              totalEngagement: metrics.total_engagement || 0,
              totalFollowers: metrics.total_followers || 0,
              engagementRate: metrics.engagement_rate || 0,
              viewsChange: metrics.views_change || 0,
              engagementChange: metrics.engagement_change || 0,
              followersChange: metrics.followers_change || 0,
              engagementRateChange: metrics.engagement_rate_change || 0
            }
          }))
        }
      } catch (error) {
        console.error('Failed to load analytics:', error)
        // Keep using mock data on error
      } finally {
        setIsLoading(false)
      }
    }

    loadAnalytics()
  }, [selectedTimeRange, selectedPlatform, showRealTime, apiService, makeAuthenticatedRequest])

  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M'
    }
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K'
    }
    return num.toLocaleString()
  }

  const getChangeIcon = (change) => {
    return change >= 0 ? (
      <ArrowUpIcon className="h-4 w-4 text-green-500" />
    ) : (
      <ArrowDownIcon className="h-4 w-4 text-red-500" />
    )
  }

  const getChangeColor = (change) => {
    return change >= 0 ? 'text-green-600' : 'text-red-600'
  }

  const platformData = {
    labels: Object.values(analyticsData.platforms).map(p => p.name),
    datasets: [
      {
        label: 'Followers',
        data: Object.values(analyticsData.platforms).map(p => p.followers),
        backgroundColor: Object.values(analyticsData.platforms).map(p => p.color + '80'),
        borderColor: Object.values(analyticsData.platforms).map(p => p.color),
        borderWidth: 2,
      }
    ]
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Analytics</h2>
          <p className="text-sm text-gray-600">
            Track performance metrics and insights across platforms
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setShowRealTime(!showRealTime)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center space-x-2 ${
              showRealTime 
                ? 'bg-green-600 text-white' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <BoltIcon className="h-4 w-4" />
            <span>Real-Time</span>
          </button>
          
          <select
            value={selectedTimeRange}
            onChange={(e) => setSelectedTimeRange(e.target.value)}
            className="text-sm border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {timeRanges.map((range) => (
              <option key={range.value} value={range.value}>
                {range.label}
              </option>
            ))}
          </select>
          
          <select
            value={selectedPlatform}
            onChange={(e) => setSelectedPlatform(e.target.value)}
            className="text-sm border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Platforms</option>
            {Object.entries(mockAnalytics.platforms).map(([key, platform]) => (
              <option key={key} value={key}>
                {platform.name}
              </option>
            ))}
          </select>
          
          <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors flex items-center space-x-2">
            <FunnelIcon className="h-4 w-4" />
            <span>Export</span>
          </button>
        </div>
      </div>

      {/* Real-Time Metrics */}
      {showRealTime && (
        <RealTimeMetrics timeframe={selectedTimeRange} />
      )}

      {/* Key Metrics Cards - Historical Data */}
      {!showRealTime && (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Total Views</p>
              <p className="text-3xl font-bold text-gray-900">
                {formatNumber(analyticsData.overview.totalViews)}
              </p>
            </div>
            <div className="p-3 bg-blue-100 rounded-full">
              <EyeIcon className="h-6 w-6 text-blue-600" />
            </div>
          </div>
          <div className="flex items-center mt-4">
            {getChangeIcon(analyticsData.overview.viewsChange)}
            <span className={`text-sm font-medium ml-1 ${getChangeColor(analyticsData.overview.viewsChange)}`}>
              {Math.abs(analyticsData.overview.viewsChange)}%
            </span>
            <span className="text-sm text-gray-500 ml-1">vs last period</span>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Total Engagement</p>
              <p className="text-3xl font-bold text-gray-900">
                {formatNumber(analyticsData.overview.totalEngagement)}
              </p>
            </div>
            <div className="p-3 bg-green-100 rounded-full">
              <HeartIcon className="h-6 w-6 text-green-600" />
            </div>
          </div>
          <div className="flex items-center mt-4">
            {getChangeIcon(analyticsData.overview.engagementChange)}
            <span className={`text-sm font-medium ml-1 ${getChangeColor(analyticsData.overview.engagementChange)}`}>
              {Math.abs(analyticsData.overview.engagementChange)}%
            </span>
            <span className="text-sm text-gray-500 ml-1">vs last period</span>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Total Followers</p>
              <p className="text-3xl font-bold text-gray-900">
                {formatNumber(analyticsData.overview.totalFollowers)}
              </p>
            </div>
            <div className="p-3 bg-purple-100 rounded-full">
              <ChatBubbleLeftIcon className="h-6 w-6 text-purple-600" />
            </div>
          </div>
          <div className="flex items-center mt-4">
            {getChangeIcon(analyticsData.overview.followersChange)}
            <span className={`text-sm font-medium ml-1 ${getChangeColor(analyticsData.overview.followersChange)}`}>
              {Math.abs(analyticsData.overview.followersChange)}%
            </span>
            <span className="text-sm text-gray-500 ml-1">vs last period</span>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Engagement Rate</p>
              <p className="text-3xl font-bold text-gray-900">
                {analyticsData.overview.engagementRate}%
              </p>
            </div>
            <div className="p-3 bg-orange-100 rounded-full">
              <ShareIcon className="h-6 w-6 text-orange-600" />
            </div>
          </div>
          <div className="flex items-center mt-4">
            {getChangeIcon(analyticsData.overview.engagementRateChange)}
            <span className={`text-sm font-medium ml-1 ${getChangeColor(analyticsData.overview.engagementRateChange)}`}>
              {Math.abs(analyticsData.overview.engagementRateChange)}%
            </span>
            <span className="text-sm text-gray-500 ml-1">vs last period</span>
          </div>
        </div>
      </div>
      )}

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Engagement Trend */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Engagement Trend</h3>
          <div className="h-64">
            <Line 
              data={analyticsData.engagementTrend}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    display: false,
                  },
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    grid: {
                      color: 'rgba(0, 0, 0, 0.05)',
                    },
                  },
                  x: {
                    grid: {
                      display: false,
                    },
                  },
                },
              }}
            />
          </div>
        </div>

        {/* Platform Distribution */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Platform Distribution</h3>
          <div className="h-64">
            <Bar 
              data={platformData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    display: false,
                  },
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    grid: {
                      color: 'rgba(0, 0, 0, 0.05)',
                    },
                  },
                  x: {
                    grid: {
                      display: false,
                    },
                  },
                },
              }}
            />
          </div>
        </div>

        {/* Content Performance */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Content Performance by Type</h3>
          <div className="h-64">
            <Doughnut 
              data={mockAnalytics.contentPerformance}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'bottom',
                    labels: {
                      padding: 20,
                      usePointStyle: true,
                    },
                  },
                },
              }}
            />
          </div>
        </div>

        {/* Top Performing Content */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Top Performing Content</h3>
          <div className="space-y-4">
            {mockAnalytics.topContent.map((content, index) => (
              <div key={content.id} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-sm font-medium text-blue-600">#{index + 1}</span>
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="text-sm font-medium text-gray-900 truncate">
                    {content.title}
                  </h4>
                  <div className="flex items-center space-x-4 mt-1 text-xs text-gray-500">
                    <span className="capitalize">{content.platform}</span>
                    <span>{formatNumber(content.views)} views</span>
                    <span>{content.engagement_rate}% engagement</span>
                  </div>
                </div>
                <div className="flex-shrink-0 text-right">
                  <div className="text-sm font-medium text-gray-900">
                    {formatNumber(content.likes + content.comments + content.shares)}
                  </div>
                  <div className="text-xs text-gray-500">interactions</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Platform Breakdown */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Platform Breakdown</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(mockAnalytics.platforms).map(([key, platform]) => (
              <div key={key} className="text-center p-4 border rounded-lg">
                <div 
                  className="w-12 h-12 rounded-full mx-auto mb-3 flex items-center justify-center text-white font-bold"
                  style={{ backgroundColor: platform.color }}
                >
                  {platform.name.charAt(0)}
                </div>
                <h4 className="font-medium text-gray-900">{platform.name}</h4>
                <div className="mt-2 space-y-1">
                  <div className="text-sm text-gray-600">
                    <span className="font-medium">{formatNumber(platform.followers)}</span> followers
                  </div>
                  <div className="text-sm text-gray-600">
                    <span className="font-medium">{formatNumber(platform.engagement)}</span> engagement
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}