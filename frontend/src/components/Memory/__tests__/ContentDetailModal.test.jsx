import { render, screen, fireEvent } from '@testing-library/react'
import ContentDetailModal from '../ContentDetailModal'

describe('ContentDetailModal', () => {
  const mockContent = {
    id: 1,
    title: 'Test Content',
    body: 'This is test content body',
    platform: 'LinkedIn',
    performance: {
      views: 1500,
      likes: 120,
      shares: 45,
      engagement_rate: 8.5
    },
    created_at: '2023-12-01T10:00:00Z',
    tags: ['AI', 'Technology', 'Innovation']
  }

  const mockProps = {
    content: mockContent,
    isOpen: true,
    onClose: jest.fn(),
    onRepurpose: jest.fn(),
    onEdit: jest.fn(),
    onDelete: jest.fn()
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders modal when open and content provided', () => {
    render(<ContentDetailModal {...mockProps} />)
    
    expect(screen.getByText('Test Content')).toBeInTheDocument()
    expect(screen.getByText('This is test content body')).toBeInTheDocument()
    expect(screen.getByText('LinkedIn')).toBeInTheDocument()
  })

  it('does not render when closed', () => {
    render(<ContentDetailModal {...mockProps} isOpen={false} />)
    
    expect(screen.queryByText('Test Content')).not.toBeInTheDocument()
  })

  it('does not render when no content provided', () => {
    render(<ContentDetailModal {...mockProps} content={null} />)
    
    expect(screen.queryByText('Test Content')).not.toBeInTheDocument()
  })

  it('displays performance metrics', () => {
    render(<ContentDetailModal {...mockProps} />)
    
    expect(screen.getByText('1,500')).toBeInTheDocument() // views
    expect(screen.getByText('120')).toBeInTheDocument() // likes
    expect(screen.getByText('45')).toBeInTheDocument() // shares
    expect(screen.getByText('8.5%')).toBeInTheDocument() // engagement rate
  })

  it('displays formatted date', () => {
    render(<ContentDetailModal {...mockProps} />)
    
    // Check that date is displayed (format may vary)
    expect(screen.getByText(/Friday/)).toBeInTheDocument()
    expect(screen.getByText(/December/)).toBeInTheDocument()
  })

  it('displays tags', () => {
    render(<ContentDetailModal {...mockProps} />)
    
    expect(screen.getByText('AI')).toBeInTheDocument()
    expect(screen.getByText('Technology')).toBeInTheDocument()
    expect(screen.getByText('Innovation')).toBeInTheDocument()
  })

  it('calls onClose when close button clicked', () => {
    render(<ContentDetailModal {...mockProps} />)
    
    const closeButton = screen.getByRole('button', { name: /close/i })
    fireEvent.click(closeButton)
    
    expect(mockProps.onClose).toHaveBeenCalled()
  })

  it('calls onEdit when edit button clicked', () => {
    render(<ContentDetailModal {...mockProps} />)
    
    const editButton = screen.getByRole('button', { name: /edit/i })
    fireEvent.click(editButton)
    
    expect(mockProps.onEdit).toHaveBeenCalledWith(mockContent)
  })

  it('calls onDelete when delete button clicked', () => {
    render(<ContentDetailModal {...mockProps} />)
    
    const deleteButton = screen.getByRole('button', { name: /delete/i })
    fireEvent.click(deleteButton)
    
    expect(mockProps.onDelete).toHaveBeenCalledWith(mockContent.id)
  })

  it('shows repurpose options when repurpose button clicked', () => {
    render(<ContentDetailModal {...mockProps} />)
    
    const repurposeButton = screen.getByRole('button', { name: /repurpose/i })
    fireEvent.click(repurposeButton)
    
    expect(screen.getByText('Twitter Thread')).toBeInTheDocument()
    expect(screen.getByText('LinkedIn Carousel')).toBeInTheDocument()
    expect(screen.getByText('Instagram Stories')).toBeInTheDocument()
  })

  it('calls onRepurpose when repurpose option selected', () => {
    render(<ContentDetailModal {...mockProps} />)
    
    // Open repurpose options
    const repurposeButton = screen.getByRole('button', { name: /repurpose/i })
    fireEvent.click(repurposeButton)
    
    // Click on Twitter Thread option
    const twitterOption = screen.getByText('Twitter Thread')
    fireEvent.click(twitterOption)
    
    expect(mockProps.onRepurpose).toHaveBeenCalledWith(
      mockContent.id,
      'twitter-thread'
    )
  })

  it('handles content without performance data', () => {
    const contentWithoutPerformance = {
      ...mockContent,
      performance: undefined
    }
    
    render(<ContentDetailModal {...mockProps} content={contentWithoutPerformance} />)
    
    expect(screen.getByText('Test Content')).toBeInTheDocument()
    // Should not crash when performance data is missing
  })

  it('handles content without tags', () => {
    const contentWithoutTags = {
      ...mockContent,
      tags: undefined
    }
    
    render(<ContentDetailModal {...mockProps} content={contentWithoutTags} />)
    
    expect(screen.getByText('Test Content')).toBeInTheDocument()
    // Should not crash when tags are missing
  })

  it('formats large numbers correctly', () => {
    const contentWithLargeNumbers = {
      ...mockContent,
      performance: {
        views: 15000,
        likes: 1200,
        shares: 450,
        engagement_rate: 12.7
      }
    }
    
    render(<ContentDetailModal {...mockProps} content={contentWithLargeNumbers} />)
    
    expect(screen.getByText('15,000')).toBeInTheDocument()
    expect(screen.getByText('1,200')).toBeInTheDocument()
    expect(screen.getByText('450')).toBeInTheDocument()
  })
})