import { useState } from 'react'
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline'

// Mock data for scheduled posts
const scheduledPosts = [
  {
    id: 1,
    title: 'Industry Trends Analysis',
    platform: 'LinkedIn',
    date: '2025-07-23',
    time: '10:00',
    status: 'scheduled',
    content: 'The future of AI in social media marketing...',
  },
  {
    id: 2,
    title: 'Quick Tips Thread',
    platform: 'Twitter',
    date: '2025-07-23',
    time: '15:00',
    status: 'scheduled',
    content: '5 ways to improve your social media engagement...',
  },
  {
    id: 3,
    title: 'Behind the Scenes',
    platform: 'Instagram',
    date: '2025-07-24',
    time: '12:00',
    status: 'draft',
    content: 'A look at our AI content creation process...',
  },
]

const platforms = {
  LinkedIn: { color: 'bg-blue-600', textColor: 'text-blue-600' },
  Twitter: { color: 'bg-sky-500', textColor: 'text-sky-500' },
  Instagram: { color: 'bg-pink-600', textColor: 'text-pink-600' },
  Facebook: { color: 'bg-indigo-600', textColor: 'text-indigo-600' },
}

export default function Calendar() {
  const [currentDate, setCurrentDate] = useState(new Date())

  const getDaysInMonth = (date) => {
    const year = date.getFullYear()
    const month = date.getMonth()
    const firstDay = new Date(year, month, 1)
    const lastDay = new Date(year, month + 1, 0)
    const daysInMonth = lastDay.getDate()
    const startingDayOfWeek = firstDay.getDay()

    const days = []
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null)
    }
    
    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(day)
    }
    
    return days
  }

  const getPostsForDate = (day) => {
    if (!day) return []
    const dateStr = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
    return scheduledPosts.filter(post => post.date === dateStr)
  }

  const navigateMonth = (direction) => {
    const newDate = new Date(currentDate)
    newDate.setMonth(newDate.getMonth() + direction)
    setCurrentDate(newDate)
  }

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ]

  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

  return (
    <div className="space-y-6">
      {/* Calendar Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
          </h2>
          <p className="text-sm text-gray-600">
            Manage your content calendar and scheduled posts
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => navigateMonth(-1)}
            className="p-2 rounded-md border border-gray-300 bg-white hover:bg-gray-50"
          >
            <ChevronLeftIcon className="h-5 w-5" />
          </button>
          <button
            onClick={() => setCurrentDate(new Date())}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Today
          </button>
          <button
            onClick={() => navigateMonth(1)}
            className="p-2 rounded-md border border-gray-300 bg-white hover:bg-gray-50"
          >
            <ChevronRightIcon className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Calendar Grid */}
      <div className="bg-white rounded-lg shadow">
        <div className="grid grid-cols-7 border-b border-gray-200">
          {dayNames.map((day) => (
            <div key={day} className="p-4 text-center text-sm font-medium text-gray-500">
              {day}
            </div>
          ))}
        </div>
        
        <div className="grid grid-cols-7">
          {getDaysInMonth(currentDate).map((day, index) => {
            const posts = getPostsForDate(day)
            const isToday = day === new Date().getDate() && 
              currentDate.getMonth() === new Date().getMonth() && 
              currentDate.getFullYear() === new Date().getFullYear()
            
            return (
              <div
                key={index}
                className={`min-h-32 p-2 border-r border-b border-gray-200 ${
                  day ? 'hover:bg-gray-50' : ''
                }`}
              >
                {day && (
                  <>
                    <div className={`text-sm font-medium ${
                      isToday ? 'text-blue-600' : 'text-gray-900'
                    }`}>
                      {isToday && (
                        <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-blue-600 text-white text-xs">
                          {day}
                        </span>
                      )}
                      {!isToday && day}
                    </div>
                    
                    <div className="mt-1 space-y-1">
                      {posts.map((post) => (
                        <div
                          key={post.id}
                          className={`text-xs p-1 rounded truncate ${
                            platforms[post.platform]?.color || 'bg-gray-500'
                          } text-white cursor-pointer hover:opacity-80`}
                          title={`${post.time} - ${post.title}`}
                        >
                          {post.time} {post.platform}
                        </div>
                      ))}
                    </div>
                  </>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* Upcoming Posts */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Upcoming Posts</h3>
        <div className="space-y-3">
          {scheduledPosts.slice(0, 5).map((post) => (
            <div key={post.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className={`w-3 h-3 rounded-full ${platforms[post.platform]?.color}`} />
                <div>
                  <p className="font-medium text-gray-900">{post.title}</p>
                  <p className="text-sm text-gray-500">{post.content.substring(0, 80)}...</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">{post.date}</p>
                <p className="text-sm text-gray-500">{post.time} • {post.platform}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}