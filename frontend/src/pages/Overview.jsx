import { useQuery } from '@tanstack/react-query'
import { useState, useEffect } from 'react'
import { 
  DocumentTextIcon,
  PlusIcon,
  SparklesIcon,
  CpuChipIcon,
  CalendarDaysIcon,
  CheckCircleIcon,
  ClockIcon,
  PhotoIcon,
  ArrowRightIcon,
  HeartIcon
} from '@heroicons/react/24/outline'
import { useEnhancedApi } from '../hooks/useEnhancedApi'
import { Link } from 'react-router-dom'

// Lily's random compliments
const compliments = [
  "Looking sharp today! 🌟",
  "Your style is on point! ✨", 
  "You have great energy today! ⚡",
  "That smile could light up a room! 😊",
  "You're absolutely glowing! ✨",
  "Your confidence is inspiring! 💫",
  "You look fantastic today! 👌",
  "That's a great look on you! 🎨",
  "You're radiating positivity! ☀️",
  "Your presence brightens the whole room! 🌈"
]

const LilyCompliment = () => {
  const [compliment, setCompliment] = useState('')
  const [showCompliment, setShowCompliment] = useState(false)

  useEffect(() => {
    // 30% chance to show a compliment on page load
    if (Math.random() < 0.3) {
      const randomCompliment = compliments[Math.floor(Math.random() * compliments.length)]
      setCompliment(randomCompliment)
      setShowCompliment(true)
      
      // Hide the compliment after 8 seconds
      const timer = setTimeout(() => {
        setShowCompliment(false)
      }, 8000)
      
      return () => clearTimeout(timer)
    }
  }, [])

  if (!showCompliment) return null

  return (
    <div className="bg-gradient-to-r from-pink-50 to-purple-50 border border-pink-200 rounded-xl p-6 mb-6 relative shadow-sm">
      <button 
        onClick={() => setShowCompliment(false)}
        className="absolute top-3 right-3 text-pink-400 hover:text-pink-600 hover:bg-pink-100 rounded-full p-1 transition-all duration-200"
      >
        ✕
      </button>
      <div className="flex items-start space-x-4">
        <div className="flex-shrink-0">
          <div className="p-3 bg-pink-100 rounded-full">
            <HeartIcon className="h-6 w-6 text-pink-500" />
          </div>
        </div>
        <div className="flex-grow">
          <div className="flex items-center mb-2">
            <span className="text-blue-600 font-semibold text-sm uppercase tracking-wide">Lily says:</span>
          </div>
          <p className="text-gray-800 text-lg font-medium leading-relaxed">
            {compliment}
          </p>
        </div>
      </div>
    </div>
  )
}

const ContentCard = ({ title, count, icon: Icon, color = "blue", description, linkTo }) => {
  const colorClasses = {
    blue: 'text-blue-600 bg-blue-100',
    green: 'text-green-600 bg-green-100',
    purple: 'text-purple-600 bg-purple-100',
    orange: 'text-orange-600 bg-orange-100',
    gray: 'text-gray-600 bg-gray-100'
  }

  return (
    <Link to={linkTo} className="group">
      <div className="bg-white rounded-lg shadow hover:shadow-md transition-shadow p-6 group-hover:border-blue-200 border border-transparent">
        <div className="flex items-center justify-between">
          <div>
            <div className={`inline-flex p-3 rounded-lg ${colorClasses[color]} mb-4`}>
              <Icon className="h-6 w-6" />
            </div>
            <p className="text-2xl font-bold text-gray-900">{count}</p>
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className="text-xs text-gray-500 mt-1">{description}</p>
          </div>
          <ArrowRightIcon className="h-5 w-5 text-gray-400 group-hover:text-blue-600 transition-colors" />
        </div>
      </div>
    </Link>
  )
}

const QuickActionCard = ({ title, description, icon: Icon, color = "blue", action, disabled = false }) => {
  const colorClasses = {
    blue: 'bg-blue-600 hover:bg-blue-700 text-white',
    purple: 'bg-purple-600 hover:bg-purple-700 text-white',
    green: 'bg-green-600 hover:bg-green-700 text-white'
  }

  return (
    <button 
      onClick={action}
      disabled={disabled}
      className={`${colorClasses[color]} rounded-lg p-6 text-left transition-colors disabled:opacity-50 disabled:cursor-not-allowed w-full`}
    >
      <div className="flex items-center mb-3">
        <Icon className="h-8 w-8 mr-3" />
        <h3 className="text-lg font-semibold">{title}</h3>
      </div>
      <p className="text-sm opacity-90">{description}</p>
    </button>
  )
}

export default function Overview() {
  const { api } = useEnhancedApi()
  
  // Fetch content statistics
  const { data: contentStats, isLoading: contentLoading } = useQuery({
    queryKey: ['content-stats'],
    queryFn: async () => {
      const content = await api.content.getAll(1, 100)
      const aiGenerated = content.filter(item => item.generated_by_ai).length
      const drafts = content.filter(item => item.status === 'draft').length
      const scheduled = content.filter(item => item.status === 'scheduled').length
      const published = content.filter(item => item.status === 'published').length
      
      return {
        total: content.length,
        aiGenerated,
        drafts,
        scheduled,
        published
      }
    },
    refetchInterval: 30 * 1000,
    retry: 2
  })

  // Fetch upcoming content
  const { data: upcomingContent } = useQuery({
    queryKey: ['upcoming-content'],
    queryFn: () => api.content.getUpcoming(),
    retry: 2
  })

  // Fetch memory stats for industry insights
  const { data: memoryStats } = useQuery({
    queryKey: ['memory-analytics'],
    queryFn: () => api.memory.getAnalytics(),
    retry: 2
  })

  const handleGenerateAIContent = async () => {
    const prompt = window.prompt('Enter a prompt for AI content generation:')
    if (prompt && prompt.trim()) {
      try {
        // This would typically be handled by a mutation, but for demo:
        alert('Redirecting to Create Post page with AI generation...')
        window.location.href = '/create-post'
      } catch (error) {
        alert('Failed to generate content. Please try again.')
      }
    }
  }

  const handleScheduleContent = () => {
    window.location.href = '/calendar'
  }

  const handleManageContent = () => {
    window.location.href = '/content'
  }

  if (contentLoading) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="h-32 bg-gray-300 rounded-lg"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-40 bg-gray-300 rounded-lg"></div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Lily's Random Compliment */}
      <LilyCompliment />
      
      {/* Lily's Introduction */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg shadow-lg p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2">👋 Hi, I'm Lily!</h1>
            <h2 className="text-2xl font-semibold mb-3 text-blue-100">Your new Social Media Manager 😊</h2>
            <p className="text-blue-100 text-lg mb-4">
              I gather the latest industry insights and trends to create professional, 
              engaging social media posts that resonate with your audience. Let me handle 
              your content creation while you focus on growing your business!
            </p>
            <div className="mt-4 flex items-center space-x-6 text-sm">
              <div>
                <span className="font-semibold">{contentStats?.total || 0}</span> Total Content Created
              </div>
              <div>
                <span className="font-semibold">{contentStats?.aiGenerated || 0}</span> Posts by Lily
              </div>
              <div>
                <span className="font-semibold">{upcomingContent?.length || 0}</span> Ready to Publish
              </div>
            </div>
          </div>
          <div className="text-right">
            <Link 
              to="/create-post"
              className="group inline-flex items-center px-8 py-4 bg-gradient-to-r from-white to-blue-50 hover:from-blue-50 hover:to-white text-blue-600 font-semibold rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 border border-white border-opacity-50 backdrop-blur-sm"
            >
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 rounded-lg mr-3 group-hover:bg-blue-200 transition-colors duration-200">
                  <PlusIcon className="h-5 w-5 text-blue-600" />
                </div>
                <span className="text-lg">Let's Create Together</span>
                <svg className="ml-2 h-5 w-5 transform group-hover:translate-x-1 transition-transform duration-200" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </div>
            </Link>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <QuickActionCard
          title="Let Lily Create"
          description="I'll craft engaging posts using the latest industry insights and trends"
          icon={SparklesIcon}
          color="purple"
          action={handleGenerateAIContent}
        />
        <QuickActionCard
          title="Schedule Content"
          description="Plan and schedule your content across platforms"
          icon={CalendarDaysIcon}
          color="blue"
          action={handleScheduleContent}
        />
        <QuickActionCard
          title="Content Library"
          description="Browse and manage all the content I've created for you"
          icon={DocumentTextIcon}
          color="green"
          action={handleManageContent}
        />
      </div>

      {/* Content Statistics */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Content Overview</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <ContentCard
            title="Draft Content"
            count={contentStats?.drafts || 0}
            icon={DocumentTextIcon}
            color="gray"
            description="Ready for review and publishing"
            linkTo="/content?status=draft"
          />
          <ContentCard
            title="AI Generated"
            count={contentStats?.aiGenerated || 0}
            icon={SparklesIcon}
            color="purple"
            description="Created with artificial intelligence"
            linkTo="/content"
          />
          <ContentCard
            title="Scheduled"
            count={contentStats?.scheduled || 0}
            icon={ClockIcon}
            color="blue"
            description="Queued for automatic publishing"
            linkTo="/calendar"
          />
          <ContentCard
            title="Published"
            count={contentStats?.published || 0}
            icon={CheckCircleIcon}
            color="green"
            description="Successfully posted content"
            linkTo="/content?status=published"
          />
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Upcoming Content */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Upcoming Content</h3>
          {upcomingContent && upcomingContent.length > 0 ? (
            <div className="space-y-3">
              {upcomingContent.slice(0, 5).map((item) => (
                <div key={item.id} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900 truncate">{item.title}</p>
                    <p className="text-xs text-gray-500">{item.platform} • {new Date(item.scheduled_at).toLocaleDateString()}</p>
                  </div>
                  {item.image_url && <PhotoIcon className="h-4 w-4 text-gray-400 ml-2" />}
                </div>
              ))}
              <Link to="/calendar" className="block text-sm text-blue-600 hover:text-blue-700 mt-3">
                View all scheduled →
              </Link>
            </div>
          ) : (
            <p className="text-gray-500 text-sm">No scheduled content. Start by creating some posts!</p>
          )}
        </div>

        {/* Lily's Capabilities */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">What I Can Do For You</h3>
          <div className="space-y-4">
            <div className="flex items-center">
              <CpuChipIcon className="h-5 w-5 text-purple-600 mr-3" />
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">Industry Research</p>
                <p className="text-xs text-gray-500">I stay up-to-date with the latest trends in your industry</p>
              </div>
              <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">Always On</span>
            </div>
            <div className="flex items-center">
              <SparklesIcon className="h-5 w-5 text-blue-600 mr-3" />
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">Content Creation</p>
                <p className="text-xs text-gray-500">Professional posts tailored to your brand and audience</p>
              </div>
              <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">Ready</span>
            </div>
            <div className="flex items-center">
              <PhotoIcon className="h-5 w-5 text-orange-600 mr-3" />
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">Visual Content</p>
                <p className="text-xs text-gray-500">Eye-catching images to complement your posts</p>
              </div>
              <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">Available</span>
            </div>
            <Link to="/create-post" className="block text-sm text-blue-600 hover:text-blue-700 mt-3">
              Let's get started together →
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}