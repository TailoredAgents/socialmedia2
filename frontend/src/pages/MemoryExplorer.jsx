import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useEnhancedApi } from '../hooks/useEnhancedApi'
import { 
  MagnifyingGlassIcon,
  FunnelIcon,
  DocumentTextIcon,
  PhotoIcon,
  ChartBarIcon,
  CalendarIcon,
  ArrowPathIcon,
  HeartIcon,
  ShareIcon,
  EyeIcon,
  ChartPieIcon,
  BoltIcon
} from '@heroicons/react/24/outline'
import SimilarityChart from '../components/Memory/SimilarityChart'
import ContentDetailModal from '../components/Memory/ContentDetailModal'

// Mock data for memory content
const mockMemoryContent = [
  {
    id: 1,
    type: 'research',
    title: 'AI Marketing Trends Analysis',
    content: 'AI marketing automation is seeing 300% growth in 2025, with personalization being the key driver...',
    platform: 'web',
    engagement: { likes: 0, shares: 0, views: 145 },
    created_at: '2025-07-22T08:00:00Z',
    tags: ['AI', 'Marketing', 'Trends'],
    similarity_score: 0.92,
    repurpose_suggestions: 3
  },
  {
    id: 2,
    type: 'content',
    title: 'LinkedIn Post: Future of Social Media',
    content: 'The future of social media is autonomous. AI agents will handle 80% of content creation by 2026...',
    platform: 'linkedin',
    engagement: { likes: 45, shares: 12, views: 890 },
    created_at: '2025-07-21T15:30:00Z',
    tags: ['Social Media', 'AI', 'Future'],
    similarity_score: 0.88,
    repurpose_suggestions: 5
  },
  {
    id: 3,
    type: 'image',
    title: 'AI Infographic - Social Media Stats',
    content: 'Visual representation of social media engagement statistics across platforms',
    platform: 'instagram',
    engagement: { likes: 234, shares: 56, views: 1250 },
    created_at: '2025-07-20T12:15:00Z',
    tags: ['Infographic', 'Statistics', 'Visual'],
    similarity_score: 0.85,
    repurpose_suggestions: 2
  },
  {
    id: 4,
    type: 'competitor_analysis',
    title: 'Buffer Content Strategy Analysis',
    content: 'Analysis of Buffer\'s recent content shows focus on educational carousels and quick tips format...',
    platform: 'research',
    engagement: { likes: 0, shares: 0, views: 67 },
    created_at: '2025-07-19T09:45:00Z',
    tags: ['Competitor', 'Strategy', 'Analysis'],
    similarity_score: 0.82,
    repurpose_suggestions: 4
  }
]

const contentTypes = [
  { value: 'all', label: 'All Content', icon: DocumentTextIcon },
  { value: 'research', label: 'Research', icon: ChartBarIcon },
  { value: 'content', label: 'Posts', icon: DocumentTextIcon },
  { value: 'image', label: 'Images', icon: PhotoIcon },
  { value: 'competitor_analysis', label: 'Analysis', icon: FunnelIcon }
]

const platforms = [
  { value: 'all', label: 'All Platforms' },
  { value: 'linkedin', label: 'LinkedIn' },
  { value: 'twitter', label: 'Twitter' },
  { value: 'instagram', label: 'Instagram' },
  { value: 'research', label: 'Research' },
  { value: 'web', label: 'Web' }
]

export default function MemoryExplorer() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedType, setSelectedType] = useState('all')
  const [selectedPlatform, setSelectedPlatform] = useState('all')
  const [sortBy, setSortBy] = useState('created_at')
  const [selectedContent, setSelectedContent] = useState(null)
  const [showDetailModal, setShowDetailModal] = useState(false)
  const [showSimilarityChart, setShowSimilarityChart] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)
  
  const { api, connectionStatus } = useEnhancedApi()
  const queryClient = useQueryClient()

  // Fetch all memory content
  const { 
    data: allMemoryContent = [], 
    isLoading: memoryLoading, 
    error: memoryError 
  } = useQuery({
    queryKey: ['memory', 'all', currentPage],
    queryFn: () => api.memory.getAll(currentPage, 20),
    staleTime: 2 * 60 * 1000,
    retry: 2,
    fallbackData: mockMemoryContent
  })

  // Search memory content
  const { 
    data: searchResults = [], 
    isLoading: searchLoading, 
    error: searchError 
  } = useQuery({
    queryKey: ['memory', 'search', searchQuery],
    queryFn: () => api.memory.search(searchQuery, 10),
    enabled: searchQuery.length > 2,
    staleTime: 1 * 60 * 1000,
    retry: 1
  })

  // Get memory analytics
  const { 
    data: memoryAnalytics, 
    isLoading: analyticsLoading 
  } = useQuery({
    queryKey: ['memory', 'analytics'],
    queryFn: api.memory.getAnalytics,
    staleTime: 5 * 60 * 1000,
    retry: 2
  })

  // Store memory mutation
  const storeMemoryMutation = useMutation({
    mutationFn: ({ content, metadata }) => api.memory.store(content, metadata),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['memory'] })
    },
    onError: (error) => {
      console.error('Failed to store memory:', error)
    }
  })

  // Update memory mutation
  const updateMemoryMutation = useMutation({
    mutationFn: ({ contentId, data }) => api.memory.update(contentId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['memory'] })
      setShowDetailModal(false)
    },
    onError: (error) => {
      console.error('Failed to update memory:', error)
    }
  })

  // Delete memory mutation
  const deleteMemoryMutation = useMutation({
    mutationFn: api.memory.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['memory'] })
      setShowDetailModal(false)
    },
    onError: (error) => {
      console.error('Failed to delete memory:', error)
    }
  })

  // Filter content based on search and filters
  useEffect(() => {
    const performSearch = async () => {
      setIsSearching(true)
      
      try {
        // If there's a search query, try FAISS similarity search first
        if (searchQuery && searchQuery.length > 2) {
          try {
            const searchResults = await makeAuthenticatedRequest(
              apiService.searchMemory,
              searchQuery,
              10
            )
            
            if (searchResults && searchResults.length > 0) {
              // Use real search results from FAISS
              let filtered = searchResults
              
              // Apply additional filters
              if (selectedType !== 'all') {
                filtered = filtered.filter(item => item.metadata?.type === selectedType)
              }
              
              if (selectedPlatform !== 'all') {
                filtered = filtered.filter(item => item.metadata?.platform === selectedPlatform)
              }
              
              setFilteredContent(filtered.map(result => ({
                id: result.content_id,
                title: result.metadata?.title || 'Untitled',
                content: result.content || '',
                type: result.metadata?.type || 'content',
                platform: result.metadata?.platform || 'unknown',
                engagement: result.metadata?.engagement || { likes: 0, shares: 0, views: 0 },
                created_at: result.created_at,
                tags: result.metadata?.tags || [],
                similarity_score: result.similarity_score,
                repurpose_suggestions: Math.floor(Math.random() * 5) + 1
              })))
              setIsSearching(false)
              return
            }
          } catch (error) {
            console.log('FAISS search not available, using local search:', error)
          }
        }
        
        // Fallback to local filtering
        let filtered = mockMemoryContent

        // Search filter
        if (searchQuery) {
          filtered = filtered.filter(item => 
            item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
            item.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
            item.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
          )
        }

        // Type filter
        if (selectedType !== 'all') {
          filtered = filtered.filter(item => item.type === selectedType)
        }

        // Platform filter
        if (selectedPlatform !== 'all') {
          filtered = filtered.filter(item => item.platform === selectedPlatform)
        }

        // Sort
        filtered.sort((a, b) => {
          switch (sortBy) {
            case 'engagement':
              return (b.engagement.likes + b.engagement.shares) - (a.engagement.likes + a.engagement.shares)
            case 'similarity':
              return b.similarity_score - a.similarity_score
            case 'repurpose':
              return b.repurpose_suggestions - a.repurpose_suggestions
            default: // created_at
              return new Date(b.created_at) - new Date(a.created_at)
          }
        })

        setFilteredContent(filtered)
      } catch (error) {
        console.error('Search failed:', error)
        setFilteredContent(mockMemoryContent)
      } finally {
        setIsSearching(false)
      }
    }

    const searchTimeout = setTimeout(performSearch, searchQuery ? 300 : 0)
    return () => clearTimeout(searchTimeout)
  }, [searchQuery, selectedType, selectedPlatform, sortBy, apiService, makeAuthenticatedRequest])

  const getTypeIcon = (type) => {
    const typeConfig = contentTypes.find(t => t.value === type)
    const Icon = typeConfig?.icon || DocumentTextIcon
    return Icon
  }

  const getEngagementTotal = (engagement) => {
    return (engagement.likes || 0) + (engagement.shares || 0)
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      time: 'short'
    })
  }

  const handleContentClick = (content) => {
    setSelectedContent(content)
    setShowDetailModal(true)
  }

  const handleNodeClick = (contentId) => {
    const content = filteredContent.find(item => item.id === contentId)
    if (content) {
      handleContentClick(content)
    }
  }

  const handleRepurpose = (content, option = null) => {
    console.log('Repurposing content:', content, 'with option:', option)
    // TODO: Implement repurpose functionality
    setShowDetailModal(false)
  }

  const handleEdit = (content) => {
    console.log('Editing content:', content)
    // TODO: Implement edit functionality
  }

  const handleDelete = (contentId) => {
    console.log('Deleting content:', contentId)
    // TODO: Implement delete functionality
    setShowDetailModal(false)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Memory Explorer</h2>
          <p className="text-sm text-gray-600">
            Search and explore your content history, research, and insights
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowSimilarityChart(!showSimilarityChart)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              showSimilarityChart 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <ChartPieIcon className="h-4 w-4 inline mr-2" />
            Similarity View
          </button>
          
          <button className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors flex items-center space-x-2">
            <BoltIcon className="h-4 w-4" />
            <span>Auto-Repurpose</span>
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search content using AI similarity..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {isSearching && (
              <div className="absolute right-3 top-3">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
              </div>
            )}
          </div>

          {/* Content Type Filter */}
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {contentTypes.map(type => (
              <option key={type.value} value={type.value}>{type.label}</option>
            ))}
          </select>

          {/* Platform Filter */}
          <select
            value={selectedPlatform}
            onChange={(e) => setSelectedPlatform(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {platforms.map(platform => (
              <option key={platform.value} value={platform.value}>{platform.label}</option>
            ))}
          </select>

          {/* Sort By */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="created_at">Latest First</option>
            <option value="engagement">Most Engaging</option>
            <option value="similarity">Most Similar</option>
            <option value="repurpose">Repurpose Ready</option>
          </select>
        </div>
      </div>

      {/* Similarity Chart */}
      {showSimilarityChart && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Content Similarity Map</h3>
          <SimilarityChart content={filteredContent} onNodeClick={handleNodeClick} />
          <p className="text-sm text-gray-500 mt-2">
            Click on nodes to view detailed content information. 
            {filteredContent.length > 0 && ` Showing ${filteredContent.length} content items.`}
          </p>
        </div>
      )}

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredContent.map((item) => {
          const Icon = getTypeIcon(item.type)
          const engagementTotal = getEngagementTotal(item.engagement)
          
          return (
            <div key={item.id} className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow">
              <div className="p-6">
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <Icon className="h-6 w-6 text-blue-600" />
                    <div>
                      <h3 className="font-semibold text-gray-900 line-clamp-1">
                        {item.title}
                      </h3>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                          {item.platform}
                        </span>
                        <span className="text-xs text-gray-500">
                          {formatDate(item.created_at)}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  {item.similarity_score && (
                    <div className="text-right">
                      <div className="text-sm font-medium text-green-600">
                        {Math.round(item.similarity_score * 100)}% match
                      </div>
                    </div>
                  )}
                </div>

                {/* Content Preview */}
                <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                  {item.content}
                </p>

                {/* Tags */}
                <div className="flex flex-wrap gap-1 mb-4">
                  {item.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="text-xs bg-blue-50 text-blue-600 px-2 py-1 rounded-full"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>

                {/* Stats */}
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-1">
                      <HeartIcon className="h-4 w-4" />
                      <span>{item.engagement.likes}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <ShareIcon className="h-4 w-4" />
                      <span>{item.engagement.shares}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <EyeIcon className="h-4 w-4" />
                      <span>{item.engagement.views}</span>
                    </div>
                  </div>

                  {item.repurpose_suggestions > 0 && (
                    <div className="flex items-center space-x-1">
                      <ArrowPathIcon className="h-4 w-4 text-green-600" />
                      <span className="text-green-600 font-medium">
                        {item.repurpose_suggestions} repurpose ideas
                      </span>
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex space-x-2 mt-4">
                  <button 
                    onClick={() => handleRepurpose(item)}
                    className="flex-1 bg-blue-600 text-white px-3 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
                  >
                    Repurpose Content
                  </button>
                  <button 
                    onClick={() => handleContentClick(item)}
                    className="px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    View Details
                  </button>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Empty State */}
      {filteredContent.length === 0 && !isSearching && (
        <div className="text-center py-12">
          <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No content found</h3>
          <p className="mt-1 text-sm text-gray-500">
            Try adjusting your search criteria or filters.
            {searchQuery && ' FAISS semantic search will be used when backend is connected.'}
          </p>
        </div>
      )}

      {/* Loading State */}
      {isSearching && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <h3 className="mt-2 text-sm font-medium text-gray-900">Searching...</h3>
          <p className="mt-1 text-sm text-gray-500">
            Finding similar content using AI-powered semantic search
          </p>
        </div>
      )}

      {/* Detail Modal */}
      <ContentDetailModal
        content={selectedContent}
        isOpen={showDetailModal}
        onClose={() => setShowDetailModal(false)}
        onRepurpose={handleRepurpose}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
    </div>
  )
}