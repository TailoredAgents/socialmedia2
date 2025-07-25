import { useState, useEffect, useMemo } from 'react'
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
  RadialLinearScale,
  Filler
} from 'chart.js'
import { Line, Bar, Doughnut, Radar } from 'react-chartjs-2'
import { 
  ArrowUpIcon, 
  ArrowDownIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  FireIcon,
  LightBulbIcon,
  ChartBarIcon,
  SparklesIcon,
  FunnelIcon,
  ClockIcon,
  CalendarIcon,
  UsersIcon,
  HashtagIcon,
  PhotoIcon,
  VideoCameraIcon,
  DocumentTextIcon,
  ArrowPathIcon,
  BoltIcon,
  PresentationChartLineIcon
} from '@heroicons/react/24/outline'
import { useRealTimeAnalytics, useRealTimePerformance, useRealTimeContent } from '../hooks/useRealTimeData'
import RealTimeMetrics from '../components/Analytics/RealTimeMetrics'
import PerformanceAlert from '../components/Analytics/PerformanceAlert'
import MetricCard from '../components/Analytics/MetricCard'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  RadialLinearScale,
  Filler
)

const timeRanges = [
  { value: '1h', label: 'Last hour' },
  { value: '24h', label: 'Last 24 hours' },
  { value: '7d', label: 'Last 7 days' },
  { value: '30d', label: 'Last 30 days' }
]

const platformColors = {
  twitter: '#1DA1F2',
  linkedin: '#0077B5',
  instagram: '#E4405F',
  facebook: '#1877F2',
  tiktok: '#000000'
}

const contentTypeIcons = {
  text: DocumentTextIcon,
  image: PhotoIcon,
  video: VideoCameraIcon,
  carousel: HashtagIcon
}

export default function PerformanceDashboard() {
  const [selectedTimeRange, setSelectedTimeRange] = useState('24h')
  const [selectedPlatform, setSelectedPlatform] = useState('all')
  const [activeView, setActiveView] = useState('overview') // overview, viral, engagement, timing
  
  const { 
    data: analyticsData, 
    isLoading: analyticsLoading, 
    error: analyticsError,
    lastUpdated: analyticsLastUpdated,
    refreshNow: refreshAnalytics 
  } = useRealTimeAnalytics(selectedTimeRange)
  
  const { 
    data: performanceData, 
    isLoading: performanceLoading, 
    error: performanceError,
    lastUpdated: performanceLastUpdated,
    refreshNow: refreshPerformance
  } = useRealTimePerformance(selectedPlatform)
  
  const { 
    data: contentData, 
    isLoading: contentLoading, 
    error: contentError,
    lastUpdated: contentLastUpdated,
    refreshNow: refreshContent
  } = useRealTimeContent()

  // Mock real-time performance data - will be replaced with actual backend data
  const [livePerformance, setLivePerformance] = useState({
    viralScore: 8.5,
    viralTrend: 12,
    topPerformers: [
      { id: 1, title: "AI Tools for Content Creation", platform: "linkedin", viralScore: 9.2, growth: 250, tier: "viral" },
      { id: 2, title: "Behind the Scenes", platform: "instagram", viralScore: 8.7, growth: 180, tier: "high" },
      { id: 3, title: "Quick Tips Thread", platform: "twitter", viralScore: 7.9, growth: 120, tier: "high" }
    ],
    engagementHeatmap: {
      monday: [2, 3, 4, 3, 5, 7, 8, 9, 8, 7, 8, 9, 8, 7, 6, 5, 4, 3, 2, 1, 1, 1, 2, 2],
      tuesday: [1, 2, 3, 3, 4, 6, 7, 8, 9, 8, 7, 8, 7, 6, 5, 4, 3, 2, 1, 1, 1, 1, 1, 2],
      wednesday: [2, 2, 3, 4, 5, 6, 8, 9, 9, 8, 9, 8, 7, 6, 5, 4, 3, 2, 2, 1, 1, 1, 2, 2],
      thursday: [1, 2, 2, 3, 4, 5, 7, 8, 8, 9, 8, 7, 6, 5, 4, 3, 2, 2, 1, 1, 1, 1, 1, 2],
      friday: [2, 2, 3, 3, 4, 5, 6, 7, 8, 8, 7, 6, 5, 4, 3, 3, 2, 2, 1, 1, 1, 1, 2, 2],
      saturday: [3, 3, 3, 4, 4, 5, 5, 6, 6, 5, 5, 4, 4, 3, 3, 3, 2, 2, 2, 2, 2, 3, 3, 3],
      sunday: [3, 3, 3, 4, 4, 5, 5, 6, 5, 5, 4, 4, 3, 3, 3, 2, 2, 2, 2, 2, 3, 3, 3, 3]
    },
    platformBreakdown: {
      twitter: { engagement: 6.5, reach: 45000, growth: 8.2 },
      linkedin: { engagement: 8.2, reach: 32000, growth: 15.4 },
      instagram: { engagement: 7.8, reach: 38000, growth: 12.1 },
      facebook: { engagement: 4.5, reach: 18000, growth: -2.3 },
      tiktok: { engagement: 9.1, reach: 62000, growth: 25.7 }
    },
    contentPerformance: {
      text: { avgEngagement: 5.2, posts: 42, topTier: 3 },
      image: { avgEngagement: 7.8, posts: 28, topTier: 8 },
      video: { avgEngagement: 9.1, posts: 15, topTier: 7 },
      carousel: { avgEngagement: 6.9, posts: 12, topTier: 4 }
    },
    predictions: {
      nextViralWindow: "Tomorrow 2-4 PM",
      recommendedContent: "Video tutorial on trending topic",
      optimalPlatform: "TikTok",
      confidence: 87
    }
  })

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setLivePerformance(prev => ({
        ...prev,
        viralScore: Math.min(10, Math.max(0, prev.viralScore + (Math.random() - 0.5) * 0.2)),
        viralTrend: Math.floor(Math.random() * 30) - 10,
        topPerformers: prev.topPerformers.map(p => ({
          ...p,
          growth: p.growth + Math.floor(Math.random() * 20) - 5
        }))
      }))
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  const handleRefreshAll = () => {
    refreshAnalytics()
    refreshPerformance()
    refreshContent()
  }

  const getViralScoreColor = (score) => {
    if (score >= 8) return 'text-red-600 bg-red-100'
    if (score >= 6) return 'text-orange-600 bg-orange-100'
    if (score >= 4) return 'text-yellow-600 bg-yellow-100'
    return 'text-gray-600 bg-gray-100'
  }

  const getTierBadge = (tier) => {
    const badges = {
      viral: { color: 'bg-red-500', icon: FireIcon, text: 'Viral' },
      high: { color: 'bg-orange-500', icon: TrendingUpIcon, text: 'High' },
      medium: { color: 'bg-yellow-500', icon: ChartBarIcon, text: 'Medium' },
      low: { color: 'bg-gray-500', icon: null, text: 'Low' }
    }
    return badges[tier] || badges.low
  }

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
    return num.toLocaleString()
  }

  // Chart configurations
  const viralTrendData = {
    labels: ['6h ago', '5h ago', '4h ago', '3h ago', '2h ago', '1h ago', 'Now'],
    datasets: [
      {
        label: 'Viral Score',
        data: [7.2, 7.5, 7.8, 8.1, 8.3, 8.4, livePerformance.viralScore],
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        fill: true,
        tension: 0.4,
      }
    ]
  }

  const platformRadarData = {
    labels: ['Engagement', 'Reach', 'Growth', 'Viral Potential', 'Consistency'],
    datasets: Object.entries(livePerformance.platformBreakdown).map(([platform, data]) => ({
      label: platform.charAt(0).toUpperCase() + platform.slice(1),
      data: [
        data.engagement,
        Math.min(10, data.reach / 10000),
        Math.min(10, (data.growth + 20) / 4),
        Math.random() * 10,
        Math.random() * 10
      ],
      borderColor: platformColors[platform],
      backgroundColor: platformColors[platform] + '20',
      pointBackgroundColor: platformColors[platform],
      pointBorderColor: '#fff',
      pointHoverBackgroundColor: '#fff',
      pointHoverBorderColor: platformColors[platform]
    }))
  }

  const contentTypeData = {
    labels: Object.keys(livePerformance.contentPerformance).map(type => 
      type.charAt(0).toUpperCase() + type.slice(1)
    ),
    datasets: [
      {
        label: 'Average Engagement',
        data: Object.values(livePerformance.contentPerformance).map(d => d.avgEngagement),
        backgroundColor: ['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6'],
        borderColor: ['#2563EB', '#059669', '#D97706', '#7C3AED'],
        borderWidth: 2
      }
    ]
  }

  const renderEngagementHeatmap = () => {
    const hours = Array.from({ length: 24 }, (_, i) => i)
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Engagement Heatmap</h3>
        <div className="overflow-x-auto">
          <div className="min-w-[600px]">
            <div className="grid grid-cols-25 gap-1">
              <div></div>
              {hours.map(hour => (
                <div key={hour} className="text-xs text-gray-500 text-center">
                  {hour}
                </div>
              ))}
              {Object.entries(livePerformance.engagementHeatmap).map(([day, values], dayIndex) => (
                <div key={day} className="contents">
                  <div className="text-xs text-gray-700 font-medium pr-2 flex items-center">
                    {days[dayIndex]}
                  </div>
                  {values.map((value, hourIndex) => {
                    const intensity = value / 10
                    return (
                      <div
                        key={`${day}-${hourIndex}`}
                        className="aspect-square rounded-sm cursor-pointer transition-all hover:ring-2 hover:ring-blue-400"
                        style={{
                          backgroundColor: `rgba(59, 130, 246, ${intensity})`,
                        }}
                        title={`${days[dayIndex]} ${hourIndex}:00 - Engagement: ${value}/10`}
                      />
                    )
                  })}
                </div>
              ))}
            </div>
            <div className="mt-4 flex items-center justify-center space-x-4 text-xs text-gray-600">
              <div className="flex items-center space-x-1">
                <div className="w-4 h-4 rounded-sm bg-blue-100"></div>
                <span>Low</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-4 h-4 rounded-sm bg-blue-300"></div>
                <span>Medium</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-4 h-4 rounded-sm bg-blue-500"></div>
                <span>High</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-4 h-4 rounded-sm bg-blue-700"></div>
                <span>Peak</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Performance Dashboard</h2>
          <p className="text-sm text-gray-600">
            Real-time performance analytics and optimization insights
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          <button
            onClick={handleRefreshAll}
            className="p-2 text-gray-600 hover:text-gray-900 transition-colors"
            title="Refresh all data"
          >
            <ArrowPathIcon className="h-5 w-5" />
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
            {Object.keys(platformColors).map((platform) => (
              <option key={platform} value={platform}>
                {platform.charAt(0).toUpperCase() + platform.slice(1)}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* View Tabs */}
      <div className="flex space-x-1 p-1 bg-gray-100 rounded-lg">
        {[
          { id: 'overview', label: 'Overview', icon: ChartBarIcon },
          { id: 'viral', label: 'Viral Tracking', icon: FireIcon },
          { id: 'engagement', label: 'Engagement', icon: UsersIcon },
          { id: 'timing', label: 'Timing Insights', icon: ClockIcon }
        ].map((view) => (
          <button
            key={view.id}
            onClick={() => setActiveView(view.id)}
            className={`flex-1 flex items-center justify-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeView === view.id
                ? 'bg-white text-blue-600 shadow'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <view.icon className="h-4 w-4" />
            <span>{view.label}</span>
          </button>
        ))}
      </div>

      {/* Real-Time Metrics Header */}
      {activeView === 'overview' && <RealTimeMetrics timeframe={selectedTimeRange} />}

      {/* Viral Tracking View */}
      {activeView === 'viral' && (
        <div className="space-y-6">
          {/* Viral Score Card */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">Viral Score Tracker</h3>
              <div className={`px-3 py-1 rounded-full text-sm font-medium flex items-center space-x-1 ${getViralScoreColor(livePerformance.viralScore)}`}>
                <FireIcon className="h-4 w-4" />
                <span>{livePerformance.viralScore.toFixed(1)}/10</span>
              </div>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="h-64">
                <Line 
                  data={viralTrendData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { display: false },
                    },
                    scales: {
                      y: {
                        beginAtZero: true,
                        max: 10,
                        grid: { color: 'rgba(0, 0, 0, 0.05)' },
                      },
                      x: {
                        grid: { display: false },
                      },
                    },
                  }}
                />
              </div>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <p className="text-sm text-gray-600">Viral Trend</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {livePerformance.viralTrend > 0 ? '+' : ''}{livePerformance.viralTrend}%
                    </p>
                  </div>
                  {livePerformance.viralTrend > 0 ? (
                    <TrendingUpIcon className="h-8 w-8 text-green-500" />
                  ) : (
                    <TrendingDownIcon className="h-8 w-8 text-red-500" />
                  )}
                </div>
                
                <div className="p-4 bg-blue-50 rounded-lg">
                  <div className="flex items-center space-x-2 mb-2">
                    <LightBulbIcon className="h-5 w-5 text-blue-600" />
                    <h4 className="font-medium text-gray-900">AI Prediction</h4>
                  </div>
                  <p className="text-sm text-gray-700">
                    Next viral window: <span className="font-medium">{livePerformance.predictions.nextViralWindow}</span>
                  </p>
                  <p className="text-sm text-gray-700 mt-1">
                    Recommended: <span className="font-medium">{livePerformance.predictions.recommendedContent}</span>
                  </p>
                  <div className="mt-2 flex items-center space-x-2">
                    <span className="text-xs text-gray-600">Confidence:</span>
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${livePerformance.predictions.confidence}%` }}
                      />
                    </div>
                    <span className="text-xs font-medium text-gray-700">{livePerformance.predictions.confidence}%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Top Viral Content */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Viral & Trending Content</h3>
            <div className="space-y-3">
              {livePerformance.topPerformers.map((content, index) => {
                const tierBadge = getTierBadge(content.tier)
                return (
                  <div key={content.id} className="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                    <div className="flex-shrink-0">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-bold ${tierBadge.color}`}>
                        {tierBadge.icon ? <tierBadge.icon className="h-5 w-5" /> : index + 1}
                      </div>
                    </div>
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">{content.title}</h4>
                      <div className="flex items-center space-x-3 mt-1 text-sm text-gray-600">
                        <span className="capitalize">{content.platform}</span>
                        <span>Viral Score: {content.viralScore}</span>
                        <span className="text-green-600 font-medium">+{content.growth}% growth</span>
                      </div>
                    </div>
                    <div className="flex-shrink-0">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${tierBadge.color} text-white`}>
                        {tierBadge.text}
                      </span>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      )}

      {/* Engagement View */}
      {activeView === 'engagement' && (
        <div className="space-y-6">
          {/* Platform Performance Radar */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Platform Performance Comparison</h3>
            <div className="h-96">
              <Radar 
                data={platformRadarData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      position: 'bottom',
                    },
                  },
                  scales: {
                    r: {
                      beginAtZero: true,
                      max: 10,
                      ticks: {
                        stepSize: 2
                      }
                    }
                  }
                }}
              />
            </div>
          </div>

          {/* Content Type Performance */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Content Type Performance</h3>
              <div className="h-64">
                <Doughnut 
                  data={contentTypeData}
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

            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Content Breakdown</h3>
              <div className="space-y-4">
                {Object.entries(livePerformance.contentPerformance).map(([type, data]) => {
                  const Icon = contentTypeIcons[type]
                  return (
                    <div key={type} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <Icon className="h-5 w-5 text-gray-600" />
                        <div>
                          <p className="font-medium text-gray-900 capitalize">{type}</p>
                          <p className="text-sm text-gray-600">{data.posts} posts</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-medium text-gray-900">{data.avgEngagement.toFixed(1)}%</p>
                        <p className="text-sm text-gray-600">{data.topTier} top tier</p>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Timing Insights View */}
      {activeView === 'timing' && (
        <div className="space-y-6">
          {renderEngagementHeatmap()}
          
          {/* Best Times to Post */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Optimal Posting Times</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(platformColors).map(([platform, color]) => (
                <div key={platform} className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-gray-900 capitalize">{platform}</h4>
                    <div 
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: color }}
                    />
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Best day:</span>
                      <span className="font-medium">Tuesday</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Peak time:</span>
                      <span className="font-medium">2:00 PM</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Engagement:</span>
                      <span className="font-medium text-green-600">+45%</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {/* AI Recommendations */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6">
            <div className="flex items-center space-x-3 mb-4">
              <SparklesIcon className="h-6 w-6 text-indigo-600" />
              <h3 className="text-lg font-medium text-gray-900">AI Timing Recommendations</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-2">Next Optimal Window</h4>
                <p className="text-2xl font-bold text-indigo-600">{livePerformance.predictions.nextViralWindow}</p>
                <p className="text-sm text-gray-600 mt-1">Platform: {livePerformance.predictions.optimalPlatform}</p>
              </div>
              <div className="bg-white rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-2">Content Recommendation</h4>
                <p className="text-sm text-gray-700">{livePerformance.predictions.recommendedContent}</p>
                <div className="mt-2 flex items-center space-x-2">
                  <span className="text-xs text-gray-600">Success probability:</span>
                  <span className="text-sm font-medium text-green-600">{livePerformance.predictions.confidence}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}