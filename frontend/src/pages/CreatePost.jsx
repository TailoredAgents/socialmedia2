import { useState, useEffect } from 'react'
import { useEnhancedApi } from '../hooks/useEnhancedApi'
import { useNotifications } from '../hooks/useNotifications'
import { error as logError } from '../utils/logger.js'
import {
  PlusIcon,
  PhotoIcon,
  DocumentTextIcon,
  CalendarIcon,
  SparklesIcon,
  EyeIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  XCircleIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline'

const platforms = [
  { value: 'twitter', label: 'Twitter', maxLength: 280 },
  { value: 'linkedin', label: 'LinkedIn', maxLength: 3000 },
  { value: 'instagram', label: 'Instagram', maxLength: 2200 },
  { value: 'facebook', label: 'Facebook', maxLength: 63206 }
]

const contentTypes = [
  { value: 'text', label: 'Text Post', icon: DocumentTextIcon },
  { value: 'image', label: 'Image + Text', icon: PhotoIcon },
  { value: 'ai_generated', label: 'AI Generated', icon: SparklesIcon }
]

export default function CreatePost() {
  const { api } = useEnhancedApi()
  const { showSuccess, showError } = useNotifications()
  
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    platform: 'twitter',
    contentType: 'text',
    scheduledFor: '',
    tags: []
  })
  
  const [isGenerating, setIsGenerating] = useState(false)
  const [isCreating, setIsCreating] = useState(false)
  const [generatedImage, setGeneratedImage] = useState(null)
  const [imagePrompt, setImagePrompt] = useState('')
  const [industryContext, setIndustryContext] = useState('')
  const [showResearchPanel, setShowResearchPanel] = useState(false)
  const [researchData, setResearchData] = useState(null)
  const [isResearching, setIsResearching] = useState(false)

  const selectedPlatform = platforms.find(p => p.value === formData.platform)
  const selectedContentType = contentTypes.find(c => c.value === formData.contentType)

  useEffect(() => {
    // Auto-conduct industry research when component mounts
    conductIndustryResearch()
  }, [])

  const conductIndustryResearch = async () => {
    setIsResearching(true)
    try {
      // Call actual research API
      const response = await api.autonomous.getLatestResearch()
      
      const researchData = {
        industry: response.industry || 'N/A',
        trends: response.trends || [],
        keyTopics: [],
        contentSuggestions: [],
        competitorInsights: response.insights || []
      }
      
      setResearchData(researchData)
      setIndustryContext(researchData.industry !== 'N/A' ? 
        `Based on current trends in ${researchData.industry}` : 
        'No research data available')
    } catch (error) {
      logError('Research failed:', error)
      showError('Failed to conduct industry research')
      // Set empty state
      setResearchData({
        industry: 'N/A',
        trends: [],
        keyTopics: [],
        contentSuggestions: [],
        competitorInsights: []
      })
      setIndustryContext('No research data available')
    } finally {
      setIsResearching(false)
    }
  }

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
    
    // Clear generated image if content type changes
    if (field === 'contentType' && value !== 'image' && value !== 'ai_generated') {
      setGeneratedImage(null)
      setImagePrompt('')
    }
  }

  const generateAIContent = async () => {
    setIsGenerating(true)
    try {
      const prompt = `Create engaging social media content for ${formData.platform} about AI Agent products. 
      Industry context: ${industryContext}
      Platform: ${formData.platform} (max ${selectedPlatform.maxLength} characters)
      Topic focus: Autonomous social media management and AI automation
      Tone: Professional but approachable
      Include relevant hashtags appropriate for the platform.`

      const response = await api.content.generate(prompt, formData.contentType)
      
      if (response.content) {
        setFormData(prev => ({
          ...prev,
          content: response.content,
          title: response.title || `AI Generated ${formData.platform} Post`
        }))
        showSuccess('AI content generated successfully!')
      }
    } catch (error) {
      logError('AI content generation failed:', error)
      showError('Failed to generate AI content')
    } finally {
      setIsGenerating(false)
    }
  }

  const generateImage = async () => {
    if (!imagePrompt && !formData.content) {
      showError('Please provide content or image prompt first')
      return
    }

    setIsGenerating(true)
    try {
      const prompt = imagePrompt || `Create a professional social media image for: ${formData.content.substring(0, 200)}`
      
      // Call image generation API
      const imageData = await api.content.generateImage(
        prompt,
        formData.content,
        formData.platform,
        industryContext
      )
      
      setGeneratedImage(imageData)
      showSuccess('Image generated successfully!')
    } catch (error) {
      logError('Image generation failed:', error)
      showError('Failed to generate image')
    } finally {
      setIsGenerating(false)
    }
  }

  const createPost = async () => {
    if (!formData.content.trim()) {
      showError('Please provide content for your post')
      return
    }

    setIsCreating(true)
    try {
      const postData = {
        ...formData,
        image_url: generatedImage?.image_url,
        image_prompt: imagePrompt,
        industry_context: industryContext,
        research_data: researchData,
        status: formData.scheduledFor ? 'scheduled' : 'draft',
        scheduled_at: formData.scheduledFor || null
      }

      await api.content.create(postData)
      
      showSuccess('Post created successfully!')
      
      // Reset form
      setFormData({
        title: '',
        content: '',
        platform: 'twitter',
        contentType: 'text',
        scheduledFor: '',
        tags: []
      })
      setGeneratedImage(null)
      setImagePrompt('')
    } catch (error) {
      logError('Post creation failed:', error)
      showError('Failed to create post')
    } finally {
      setIsCreating(false)
    }
  }

  const getCharacterCount = () => {
    return formData.content.length
  }

  const getCharacterCountColor = () => {
    const count = getCharacterCount()
    const maxLength = selectedPlatform.maxLength
    const percentage = count / maxLength
    
    if (percentage > 0.9) return 'text-red-600'
    if (percentage > 0.7) return 'text-yellow-600'
    return 'text-gray-600'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Create Post</h2>
          <p className="text-sm text-gray-600">
            Create engaging content with AI assistance and industry research
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowResearchPanel(!showResearchPanel)}
            className="bg-purple-600 text-white px-4 py-2 rounded-md flex items-center space-x-2 hover:bg-purple-700 transition-colors"
          >
            <InformationCircleIcon className="h-4 w-4" />
            <span>Research Insights</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content Creation */}
        <div className="lg:col-span-2 space-y-6">
          {/* Content Type & Platform Selection */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Post Configuration</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Content Type
                </label>
                <div className="space-y-2">
                  {contentTypes.map(type => (
                    <label key={type.value} className="flex items-center">
                      <input
                        type="radio"
                        name="contentType"
                        value={type.value}
                        checked={formData.contentType === type.value}
                        onChange={(e) => handleChange('contentType', e.target.value)}
                        className="mr-3"
                      />
                      <type.icon className="h-4 w-4 mr-2" />
                      <span className="text-sm">{type.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Platform
                </label>
                <select
                  value={formData.platform}
                  onChange={(e) => handleChange('platform', e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {platforms.map(platform => (
                    <option key={platform.value} value={platform.value}>
                      {platform.label} (max {platform.maxLength} chars)
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Content Creation */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">Content</h3>
              <button
                onClick={generateAIContent}
                disabled={isGenerating}
                className="bg-blue-600 text-white px-4 py-2 rounded-md flex items-center space-x-2 hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {isGenerating ? (
                  <ArrowPathIcon className="h-4 w-4 animate-spin" />
                ) : (
                  <SparklesIcon className="h-4 w-4" />
                )}
                <span>{isGenerating ? 'Generating...' : 'Generate AI Content'}</span>
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Title (Optional)
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => handleChange('title', e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Post title..."
                />
              </div>

              <div>
                <div className="flex justify-between items-center mb-1">
                  <label className="block text-sm font-medium text-gray-700">
                    Content
                  </label>
                  <span className={`text-xs ${getCharacterCountColor()}`}>
                    {getCharacterCount()}/{selectedPlatform.maxLength}
                  </span>
                </div>
                <textarea
                  value={formData.content}
                  onChange={(e) => handleChange('content', e.target.value)}
                  rows={6}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Write your content here or use AI generation..."
                  maxLength={selectedPlatform.maxLength}
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Schedule For (Optional)
                </label>
                <input
                  type="datetime-local"
                  value={formData.scheduledFor}
                  onChange={(e) => handleChange('scheduledFor', e.target.value)}
                  min={new Date().toISOString().slice(0, 16)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Image Generation */}
          {(formData.contentType === 'image' || formData.contentType === 'ai_generated') && (
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium text-gray-900">Image Generation</h3>
                <button
                  onClick={generateImage}
                  disabled={isGenerating}
                  className="bg-green-600 text-white px-4 py-2 rounded-md flex items-center space-x-2 hover:bg-green-700 transition-colors disabled:opacity-50"
                >
                  {isGenerating ? (
                    <ArrowPathIcon className="h-4 w-4 animate-spin" />
                  ) : (
                    <PhotoIcon className="h-4 w-4" />
                  )}
                  <span>{isGenerating ? 'Generating...' : 'Generate Image'}</span>
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Image Prompt (Optional - AI will generate from content if empty)
                  </label>
                  <textarea
                    value={imagePrompt}
                    onChange={(e) => setImagePrompt(e.target.value)}
                    rows={3}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Describe the image you want to generate..."
                  />
                </div>

                {generatedImage && (
                  <div className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">Generated Image</span>
                      <div className="flex items-center space-x-2">
                        {generatedImage.status === 'success' ? (
                          <CheckCircleIcon className="h-4 w-4 text-green-500" />
                        ) : (
                          <XCircleIcon className="h-4 w-4 text-red-500" />
                        )}
                        <span className="text-xs text-gray-600">
                          {generatedImage.model || 'AI Generated'}
                        </span>
                      </div>
                    </div>
                    
                    {generatedImage.image_url && (
                      <img
                        src={generatedImage.image_url}
                        alt="Generated content"
                        className="w-full max-w-md rounded-lg shadow-sm"
                      />
                    )}
                    
                    {generatedImage.error && (
                      <p className="text-sm text-red-600 mt-2">
                        {generatedImage.error}
                      </p>
                    )}
                    
                    <p className="text-xs text-gray-500 mt-2">
                      Prompt: {generatedImage.prompt}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center">
              <div className="text-sm text-gray-600">
                Ready to create your post?
              </div>
              <div className="flex space-x-3">
                <button
                  onClick={() => {
                    setFormData({
                      title: '',
                      content: '',
                      platform: 'twitter',
                      contentType: 'text',
                      scheduledFor: '',
                      tags: []
                    })
                    setGeneratedImage(null)
                    setImagePrompt('')
                  }}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
                >
                  Clear
                </button>
                <button
                  onClick={createPost}
                  disabled={isCreating || !formData.content.trim()}
                  className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center space-x-2"
                >
                  {isCreating ? (
                    <ArrowPathIcon className="h-4 w-4 animate-spin" />
                  ) : (
                    <PlusIcon className="h-4 w-4" />
                  )}
                  <span>{isCreating ? 'Creating...' : 'Create Post'}</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Research Panel */}
        <div className="lg:col-span-1">
          <div className={`bg-white rounded-lg shadow p-6 transition-all duration-300 ${showResearchPanel ? 'block' : 'hidden lg:block'}`}>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">Industry Research</h3>
              <button
                onClick={conductIndustryResearch}
                disabled={isResearching}
                className="text-blue-600 hover:text-blue-700 text-sm"
              >
                {isResearching ? 'Researching...' : 'Refresh'}
              </button>
            </div>

            {isResearching ? (
              <div className="text-center py-8">
                <ArrowPathIcon className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-2" />
                <p className="text-sm text-gray-600">Conducting industry research...</p>
              </div>
            ) : researchData ? (
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Current Trends</h4>
                  <ul className="text-sm text-gray-600 space-y-1">
                    {researchData.trends.map((trend, index) => (
                      <li key={index} className="flex items-start">
                        <span className="mr-2">•</span>
                        <span>{trend}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Content Suggestions</h4>
                  <ul className="text-sm text-gray-600 space-y-1">
                    {researchData.contentSuggestions.map((suggestion, index) => (
                      <li key={index} className="flex items-start">
                        <span className="mr-2">💡</span>
                        <span>{suggestion}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Key Topics</h4>
                  <div className="flex flex-wrap gap-2">
                    {researchData.keyTopics.map((topic, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full cursor-pointer hover:bg-blue-200"
                        onClick={() => setImagePrompt(prev => prev + (prev ? ', ' : '') + topic)}
                      >
                        {topic}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="border-t pt-4">
                  <p className="text-xs text-gray-500">
                    <strong>Industry Context:</strong> {industryContext}
                  </p>
                </div>
              </div>
            ) : (
              <p className="text-sm text-gray-600">No research data available</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}