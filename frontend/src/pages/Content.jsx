import { useState, useEffect, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useEnhancedApi } from '../hooks/useEnhancedApi'
import { error as logError } from '../utils/logger.js'
import VirtualizedContentList, { VirtualizedContentGrid } from '../components/VirtualizedContentList'
import { 
  PlusIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  CalendarIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  ShareIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  DocumentTextIcon,
  PhotoIcon,
  PlayIcon
} from '@heroicons/react/24/outline'

const contentTypes = [
  { value: 'all', label: 'All Types' },
  { value: 'text', label: 'Text Posts' },
  { value: 'image', label: 'Images' },
  { value: 'video', label: 'Videos' },
  { value: 'carousel', label: 'Carousels' }
]

const platforms = [
  { value: 'all', label: 'All Platforms' },
  { value: 'twitter', label: 'Twitter' },
  { value: 'linkedin', label: 'LinkedIn' },
  { value: 'instagram', label: 'Instagram' },
  { value: 'facebook', label: 'Facebook' }
]

const statusOptions = [
  { value: 'all', label: 'All Status' },
  { value: 'draft', label: 'Draft' },
  { value: 'scheduled', label: 'Scheduled' },
  { value: 'published', label: 'Published' },
  { value: 'failed', label: 'Failed' }
]

export default function Content() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedType, setSelectedType] = useState('all')
  const [selectedPlatform, setSelectedPlatform] = useState('all')
  const [selectedStatus, setSelectedStatus] = useState('all')
  const [selectedContent, setSelectedContent] = useState(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [editingContent, setEditingContent] = useState(null)
  const [viewMode, setViewMode] = useState('grid') // 'grid' or 'list'
  
  const { api } = useEnhancedApi()
  const queryClient = useQueryClient()

  // Fetch content with filters
  const { 
    data: content = [], 
    isLoading, 
    error, 
    refetch 
  } = useQuery({
    queryKey: ['content', selectedType, selectedPlatform, selectedStatus, searchQuery],
    queryFn: () => api.content.getAll(1, 50),
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 2
  })

  // Fetch upcoming content
  const { data: upcomingContent } = useQuery({
    queryKey: ['upcoming-content'],
    queryFn: () => api.content.getUpcoming(),
    staleTime: 60 * 1000, // 1 minute
    retry: 2
  })

  // Get content analytics
  const { data: contentAnalytics } = useQuery({
    queryKey: ['content-analytics'],
    queryFn: () => api.content.getAnalytics ? api.content.getAnalytics() : Promise.resolve({}),
    staleTime: 5 * 60 * 1000,
    retry: 1
  })

  // Delete content mutation
  const deleteContentMutation = useMutation({
    mutationFn: api.content.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['content'] })
      queryClient.invalidateQueries({ queryKey: ['upcoming-content'] })
    }
  })

  // Update content mutation
  const updateContentMutation = useMutation({
    mutationFn: ({ id, data }) => api.content.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['content'] })
      queryClient.invalidateQueries({ queryKey: ['upcoming-content'] })
      setShowEditModal(false)
      setEditingContent(null)
    },
    onError: (error) => {
      logError('Failed to update content:', error)
    }
  })

  // Publish content mutation
  const publishContentMutation = useMutation({
    mutationFn: (contentId) => api.content.update(contentId, { status: 'published' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['content'] })
      queryClient.invalidateQueries({ queryKey: ['upcoming-content'] })
    }
  })

  // Generate content mutation
  const generateContentMutation = useMutation({
    mutationFn: ({ prompt, contentType }) => api.content.generate(prompt, contentType),
    onSuccess: (newContent) => {
      queryClient.invalidateQueries({ queryKey: ['content'] })
      // Optionally show the generated content
    }
  })

  const filteredContent = useMemo(() => {
    return content.filter(item => {
      const matchesSearch = !searchQuery || 
        item.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.content?.toLowerCase().includes(searchQuery.toLowerCase())
      
      const matchesType = selectedType === 'all' || item.content_type === selectedType
      const matchesPlatform = selectedPlatform === 'all' || item.platform === selectedPlatform
      const matchesStatus = selectedStatus === 'all' || item.status === selectedStatus
      
      return matchesSearch && matchesType && matchesPlatform && matchesStatus
    })
  }, [content, searchQuery, selectedType, selectedPlatform, selectedStatus])

  // Use virtualization for large lists (more than 20 items)
  const shouldVirtualize = filteredContent.length > 20

  // Memoized helper functions for virtualization
  const getStatusIcon = useMemo(() => (status) => {
    switch (status) {
      case 'published':
        return <CheckCircleIcon className="h-4 w-4 text-green-500" />
      case 'scheduled':
        return <ClockIcon className="h-4 w-4 text-blue-500" />
      case 'failed':
        return <ExclamationTriangleIcon className="h-4 w-4 text-red-500" />
      default:
        return <DocumentTextIcon className="h-4 w-4 text-gray-500" />
    }
  }, [])

  const getStatusColor = useMemo(() => (status) => {
    switch (status) {
      case 'published':
        return 'bg-green-100 text-green-800'
      case 'scheduled':
        return 'bg-blue-100 text-blue-800'
      case 'draft':
        return 'bg-gray-100 text-gray-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }, [])

  const getContentTypeIcon = useMemo(() => (type) => {
    switch (type) {
      case 'image':
        return <PhotoIcon className="h-4 w-4" />
      case 'video':
        return <PlayIcon className="h-4 w-4" />
      default:
        return <DocumentTextIcon className="h-4 w-4" />
    }
  }, [])

  const formatDate = useMemo(() => (dateString) => {
    if (!dateString) return 'Not scheduled'
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }, [])

  const handleDeleteContent = async (contentId) => {
    if (window.confirm('Are you sure you want to delete this content?')) {
      try {
        await deleteContentMutation.mutateAsync(contentId)
      } catch (error) {
        logError('Failed to delete content:', error)
      }
    }
  }

  const handlePublishContent = async (contentId) => {
    try {
      await publishContentMutation.mutateAsync(contentId)
    } catch (error) {
      logError('Failed to publish content:', error)
    }
  }

  const handleGenerateContent = async () => {
    const prompt = window.prompt('Enter a prompt for content generation:')
    if (prompt) {
      try {
        await generateContentMutation.mutateAsync({ 
          prompt, 
          contentType: 'text' 
        })
      } catch (error) {
        logError('Failed to generate content:', error)
      }
    }
  }

  // Event handlers for virtualized list
  const handleViewContent = (item) => {
    setSelectedContent(item)
  }

  const handleEditContent = (item) => {
    setEditingContent(item)
    setShowEditModal(true)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Content Library</h2>
          <p className="text-sm text-gray-600">
            Manage your content across all platforms
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={handleGenerateContent}
            className="bg-purple-600 text-white px-4 py-2 rounded-md flex items-center space-x-2 hover:bg-purple-700 transition-colors"
          >
            <DocumentTextIcon className="h-4 w-4" />
            <span>Generate AI Content</span>
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md flex items-center space-x-2 hover:bg-blue-700 transition-colors"
          >
            <PlusIcon className="h-4 w-4" />
            <span>Create Content</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-gray-900">{content.length}</div>
          <div className="text-sm text-gray-600">Total Content</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-blue-600">
            {content.filter(c => c.status === 'scheduled').length}
          </div>
          <div className="text-sm text-gray-600">Scheduled</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-green-600">
            {content.filter(c => c.status === 'published').length}
          </div>
          <div className="text-sm text-gray-600">Published</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-gray-600">
            {content.filter(c => c.status === 'draft').length}
          </div>
          <div className="text-sm text-gray-600">Drafts</div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex-1 min-w-64">
            <div className="relative">
              <MagnifyingGlassIcon className="h-5 w-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search content..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {contentTypes.map(type => (
              <option key={type.value} value={type.value}>{type.label}</option>
            ))}
          </select>
          
          <select
            value={selectedPlatform}
            onChange={(e) => setSelectedPlatform(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {platforms.map(platform => (
              <option key={platform.value} value={platform.value}>{platform.label}</option>
            ))}
          </select>
          
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {statusOptions.map(status => (
              <option key={status.value} value={status.value}>{status.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Content Grid/List */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="bg-white rounded-lg shadow p-6 animate-pulse">
              <div className="h-4 bg-gray-200 rounded mb-4"></div>
              <div className="h-20 bg-gray-200 rounded mb-4"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      ) : filteredContent.length > 0 ? (
        shouldVirtualize ? (
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between mb-4">
              <div className="text-sm text-gray-600">
                Showing {filteredContent.length} items (virtualized for performance)
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`px-3 py-1 text-xs rounded ${
                    viewMode === 'grid' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'
                  }`}
                >
                  Grid
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`px-3 py-1 text-xs rounded ${
                    viewMode === 'list' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'
                  }`}
                >
                  List
                </button>
              </div>
            </div>
            {viewMode === 'grid' ? (
              <VirtualizedContentGrid
                items={filteredContent}
                onView={handleViewContent}
                onEdit={handleEditContent}
                onPublish={handlePublishContent}
                onDelete={handleDeleteContent}
                formatDate={formatDate}
                getStatusIcon={getStatusIcon}
                getStatusColor={getStatusColor}
                getContentTypeIcon={getContentTypeIcon}
                height={600}
                itemHeight={280}
                itemsPerRow={3}
              />
            ) : (
              <VirtualizedContentList
                items={filteredContent}
                onView={handleViewContent}
                onEdit={handleEditContent}
                onPublish={handlePublishContent}
                onDelete={handleDeleteContent}
                formatDate={formatDate}
                getStatusIcon={getStatusIcon}
                getStatusColor={getStatusColor}
                getContentTypeIcon={getContentTypeIcon}
                height={600}
                itemHeight={120}
              />
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredContent.map((item) => (
              <div key={item.id} className="bg-white rounded-lg shadow hover:shadow-md transition-shadow">
                <div className="p-6">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      {getContentTypeIcon(item.content_type)}
                      <span className="text-sm font-medium text-gray-600 capitalize">
                        {item.content_type || 'text'}
                      </span>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(item.status)}`}>
                      {item.status}
                    </span>
                  </div>
                  
                  <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2">
                    {item.title || 'Untitled'}
                  </h3>
                  
                  <p className="text-sm text-gray-600 mb-4 line-clamp-3">
                    {item.content || 'No content preview available'}
                  </p>
                  
                  <div className="flex items-center justify-between text-xs text-gray-500 mb-4">
                    <span className="capitalize">{item.platform || 'All platforms'}</span>
                    <span>{formatDate(item.scheduled_at || item.created_at)}</span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2 text-xs text-gray-500">
                      {getStatusIcon(item.status)}
                      <span>{item.performance?.views || 0} views</span>
                    </div>
                    
                    <div className="flex items-center space-x-1">
                      <button
                        onClick={() => handleViewContent(item)}
                        className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
                        title="View"
                      >
                        <EyeIcon className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleEditContent(item)}
                        className="p-1 text-gray-400 hover:text-green-600 transition-colors"
                        title="Edit"
                      >
                        <PencilIcon className="h-4 w-4" />
                      </button>
                      {item.status === 'draft' && (
                        <button
                          onClick={() => handlePublishContent(item.id)}
                          className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
                          title="Publish"
                        >
                          <ShareIcon className="h-4 w-4" />
                        </button>
                      )}
                      <button
                        onClick={() => handleDeleteContent(item.id)}
                        className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                        title="Delete"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )
      ) : (
        <div className="text-center py-12">
          <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No content found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchQuery || selectedType !== 'all' || selectedPlatform !== 'all' || selectedStatus !== 'all'
              ? 'Try adjusting your filters or search query.'
              : 'Get started by creating your first piece of content.'
            }
          </p>
          <div className="mt-6">
            <button
              onClick={() => setShowCreateModal(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              <PlusIcon className="-ml-1 mr-2 h-5 w-5" />
              Create Content
            </button>
          </div>
        </div>
      )}

      {/* Edit Content Modal */}
      {showEditModal && editingContent && (
        <ContentEditModal
          content={editingContent}
          isOpen={showEditModal}
          onClose={() => {
            setShowEditModal(false)
            setEditingContent(null)
          }}
          onSave={(updatedContent) => {
            updateContentMutation.mutate({
              id: editingContent.id,
              data: updatedContent
            })
          }}
          isLoading={updateContentMutation.isPending}
        />
      )}
    </div>
  )
}

// Simple Content Edit Modal Component
function ContentEditModal({ content, isOpen, onClose, onSave, isLoading }) {
  const [formData, setFormData] = useState({
    title: content.title || '',
    content: content.content || '',
    platform: content.platform || 'twitter',
    type: content.type || 'text',
    status: content.status || 'draft',
    scheduled_for: content.scheduled_for || ''
  })

  if (!isOpen) return null

  const handleSubmit = (e) => {
    e.preventDefault()
    onSave(formData)
  }

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        {/* Backdrop */}
        <div 
          className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" 
          onClick={onClose}
        ></div>

        {/* Modal */}
        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
          <form onSubmit={handleSubmit}>
            <div className="bg-white px-4 pt-5 pb-4 sm:p-6">
              <div className="flex items-start justify-between mb-6">
                <h3 className="text-lg font-medium text-gray-900">
                  Edit Content
                </h3>
                <button
                  type="button"
                  onClick={onClose}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <span className="sr-only">Close</span>
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="space-y-4">
                {/* Title */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Title
                  </label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => handleChange('title', e.target.value)}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Content title..."
                  />
                </div>

                {/* Content */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Content
                  </label>
                  <textarea
                    value={formData.content}
                    onChange={(e) => handleChange('content', e.target.value)}
                    rows={6}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Write your content here..."
                    required
                  />
                </div>

                {/* Platform and Type */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Platform
                    </label>
                    <select
                      value={formData.platform}
                      onChange={(e) => handleChange('platform', e.target.value)}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="twitter">Twitter</option>
                      <option value="linkedin">LinkedIn</option>
                      <option value="instagram">Instagram</option>
                      <option value="facebook">Facebook</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Type
                    </label>
                    <select
                      value={formData.type}
                      onChange={(e) => handleChange('type', e.target.value)}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="text">Text Post</option>
                      <option value="image">Image</option>
                      <option value="video">Video</option>
                      <option value="carousel">Carousel</option>
                    </select>
                  </div>
                </div>

                {/* Status */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Status
                  </label>
                  <select
                    value={formData.status}
                    onChange={(e) => handleChange('status', e.target.value)}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="draft">Draft</option>
                    <option value="scheduled">Scheduled</option>
                    <option value="published">Published</option>
                  </select>
                </div>

                {/* Scheduled Date (only show if status is scheduled) */}
                {formData.status === 'scheduled' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Scheduled For
                    </label>
                    <input
                      type="datetime-local"
                      value={formData.scheduled_for}
                      onChange={(e) => handleChange('scheduled_for', e.target.value)}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                )}
              </div>
            </div>

            {/* Footer */}
            <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button
                type="submit"
                disabled={isLoading}
                className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Saving...' : 'Save Changes'}
              </button>
              <button
                type="button"
                onClick={onClose}
                className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}