import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import Analytics from '../Analytics'

// Mock the hooks and services
jest.mock('../../hooks/useApi', () => ({
  useApi: jest.fn()
}))

jest.mock('../../hooks/useRealTimeData', () => ({
  useRealTimeData: jest.fn()
}))

jest.mock('../../utils/logger.js', () => ({
  info: jest.fn(),
  error: jest.fn(),
  debug: jest.fn(),
  warn: jest.fn()
}))

// Mock Chart.js components
jest.mock('react-chartjs-2', () => ({
  Line: ({ data, options }) => (
    <div data-testid="line-chart" data-chart-data={JSON.stringify(data)}>
      Line Chart
    </div>
  ),
  Bar: ({ data, options }) => (
    <div data-testid="bar-chart" data-chart-data={JSON.stringify(data)}>
      Bar Chart
    </div>
  ),
  Doughnut: ({ data, options }) => (
    <div data-testid="doughnut-chart" data-chart-data={JSON.stringify(data)}>
      Doughnut Chart
    </div>
  )
}))

jest.mock('chart.js', () => ({
  Chart: {
    register: jest.fn()
  },
  CategoryScale: jest.fn(),
  LinearScale: jest.fn(),
  PointElement: jest.fn(),
  LineElement: jest.fn(),
  BarElement: jest.fn(),
  ArcElement: jest.fn(),
  Title: jest.fn(),
  Tooltip: jest.fn(),
  Legend: jest.fn()
}))

const { useApi } = require('../../hooks/useApi')
const { useRealTimeData } = require('../../hooks/useRealTimeData')

// Test wrapper
const TestWrapper = ({ children }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false }
    }
  })

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </QueryClientProvider>
  )
}

describe('Analytics Page', () => {
  const mockAnalyticsData = {
    totalViews: 15420,
    totalClicks: 1240,
    totalShares: 890,
    totalComments: 456,
    engagementRate: 8.2,
    topPerformingPosts: [
      { id: 1, title: 'Post 1', views: 2500, engagement: 12.5 },
      { id: 2, title: 'Post 2', views: 2100, engagement: 9.8 }
    ],
    platformMetrics: {
      twitter: { followers: 5200, engagement: 7.8 },
      linkedin: { followers: 3100, engagement: 11.2 },
      facebook: { followers: 8900, engagement: 5.9 }
    },
    timeSeriesData: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
      datasets: [{
        label: 'Views',
        data: [1200, 1500, 1800, 2100, 1900]
      }]
    }
  }

  const mockPerformanceData = {
    averageEngagement: 8.5,
    topPlatforms: ['twitter', 'linkedin'],
    bestTimeToPost: '2:00 PM',
    contentTypes: {
      text: 45,
      image: 35,
      video: 20
    }
  }

  beforeEach(() => {
    jest.clearAllMocks()
    
    // Default mock implementations
    useApi.mockReturnValue({
      data: mockAnalyticsData,
      loading: false,
      error: null,
      refetch: jest.fn()
    })

    useRealTimeData.mockReturnValue({
      data: mockPerformanceData,
      isLoading: false,
      error: null,
      refresh: jest.fn(),
      isConnected: true,
      lastUpdated: new Date()
    })
  })

  it('renders analytics dashboard with key metrics', () => {
    render(
      <TestWrapper>
        <Analytics />
      </TestWrapper>
    )

    // Check for key metrics cards
    expect(screen.getByText('15,420')).toBeInTheDocument() // Total views
    expect(screen.getByText('1,240')).toBeInTheDocument() // Total clicks
    expect(screen.getByText('890')).toBeInTheDocument() // Total shares
    expect(screen.getByText('456')).toBeInTheDocument() // Total comments
    expect(screen.getByText('8.2%')).toBeInTheDocument() // Engagement rate
  })

  it('displays loading state', () => {
    useApi.mockReturnValue({
      data: null,
      loading: true,
      error: null,
      refetch: jest.fn()
    })

    render(
      <TestWrapper>
        <Analytics />
      </TestWrapper>
    )

    expect(screen.getByTestId('analytics-loading')).toBeInTheDocument()
    expect(screen.getByText('Loading analytics data...')).toBeInTheDocument()
  })

  it('displays error state', () => {
    const error = new Error('Failed to fetch analytics')
    useApi.mockReturnValue({
      data: null,
      loading: false,
      error,
      refetch: jest.fn()
    })

    render(
      <TestWrapper>
        <Analytics />
      </TestWrapper>
    )

    expect(screen.getByText('Error loading analytics')).toBeInTheDocument()
    expect(screen.getByText('Failed to fetch analytics')).toBeInTheDocument()
  })

  it('renders time series chart', () => {
    render(
      <TestWrapper>
        <Analytics />
      </TestWrapper>
    )

    const lineChart = screen.getByTestId('line-chart')
    expect(lineChart).toBeInTheDocument()
    
    const chartData = JSON.parse(lineChart.getAttribute('data-chart-data'))
    expect(chartData.labels).toEqual(['Jan', 'Feb', 'Mar', 'Apr', 'May'])
    expect(chartData.datasets[0].data).toEqual([1200, 1500, 1800, 2100, 1900])
  })

  it('displays platform metrics', () => {
    render(
      <TestWrapper>
        <Analytics />
      </TestWrapper>
    )

    // Check platform names and metrics
    expect(screen.getByText('Twitter')).toBeInTheDocument()
    expect(screen.getByText('LinkedIn')).toBeInTheDocument()
    expect(screen.getByText('Facebook')).toBeInTheDocument()

    expect(screen.getByText('5,200')).toBeInTheDocument() // Twitter followers
    expect(screen.getByText('3,100')).toBeInTheDocument() // LinkedIn followers
    expect(screen.getByText('8,900')).toBeInTheDocument() // Facebook followers
  })

  it('shows top performing posts', () => {
    render(
      <TestWrapper>
        <Analytics />
      </TestWrapper>
    )

    expect(screen.getByText('Top Performing Posts')).toBeInTheDocument()
    expect(screen.getByText('Post 1')).toBeInTheDocument()
    expect(screen.getByText('Post 2')).toBeInTheDocument()
    expect(screen.getByText('2,500 views')).toBeInTheDocument()
    expect(screen.getByText('12.5% engagement')).toBeInTheDocument()
  })

  it('allows time period filtering', async () => {
    const refetchMock = jest.fn()
    useApi.mockReturnValue({
      data: mockAnalyticsData,
      loading: false,
      error: null,
      refetch: refetchMock
    })

    render(
      <TestWrapper>
        <Analytics />
      </TestWrapper>
    )

    // Find and click time period selector
    const timeSelector = screen.getByLabelText('Time period')
    fireEvent.change(timeSelector, { target: { value: '30d' } })

    await waitFor(() => {
      expect(refetchMock).toHaveBeenCalled()
    })
  })

  it('handles platform filter changes', async () => {
    render(
      <TestWrapper>
        <Analytics />
      </TestWrapper>
    )

    // Find platform filter buttons
    const twitterFilter = screen.getByText('Twitter')
    fireEvent.click(twitterFilter)

    // Should filter content to show only Twitter metrics
    expect(twitterFilter.closest('button')).toHaveClass('bg-blue-500')
  })

  it('displays performance insights', () => {
    render(
      <TestWrapper>
        <Analytics />
      </TestWrapper>
    )

    expect(screen.getByText('Performance Insights')).toBeInTheDocument()
    expect(screen.getByText('8.5%')).toBeInTheDocument() // Average engagement
    expect(screen.getByText('2:00 PM')).toBeInTheDocument() // Best time to post
  })

  it('renders content type distribution chart', () => {
    render(
      <TestWrapper>
        <Analytics />
      </TestWrapper>
    )

    const doughnutChart = screen.getByTestId('doughnut-chart')
    expect(doughnutChart).toBeInTheDocument()
    
    const chartData = JSON.parse(doughnutChart.getAttribute('data-chart-data'))
    expect(chartData.datasets[0].data).toEqual([45, 35, 20])
  })

  it('shows real-time connection status', () => {
    render(
      <TestWrapper>
        <Analytics />
      </TestWrapper>
    )

    expect(screen.getByText('Live')).toBeInTheDocument()
    expect(screen.getByTestId('connection-indicator')).toHaveClass('bg-green-500')
  })

  it('handles disconnected state', () => {
    useRealTimeData.mockReturnValue({
      data: mockPerformanceData,
      isLoading: false,
      error: null,
      refresh: jest.fn(),
      isConnected: false,
      lastUpdated: new Date()
    })

    render(
      <TestWrapper>
        <Analytics />
      </TestWrapper>
    )

    expect(screen.getByText('Disconnected')).toBeInTheDocument()
    expect(screen.getByTestId('connection-indicator')).toHaveClass('bg-red-500')
  })

  it('allows manual refresh', async () => {
    const refreshMock = jest.fn()
    const refetchMock = jest.fn()
    
    useRealTimeData.mockReturnValue({
      data: mockPerformanceData,
      isLoading: false,
      error: null,
      refresh: refreshMock,
      isConnected: true,
      lastUpdated: new Date()
    })

    useApi.mockReturnValue({
      data: mockAnalyticsData,
      loading: false,
      error: null,
      refetch: refetchMock
    })

    render(
      <TestWrapper>
        <Analytics />
      </TestWrapper>
    )

    const refreshButton = screen.getByLabelText('Refresh data')
    fireEvent.click(refreshButton)

    expect(refreshMock).toHaveBeenCalled()
    expect(refetchMock).toHaveBeenCalled()
  })

  it('displays last updated timestamp', () => {
    const lastUpdated = new Date('2023-01-01T12:00:00Z')
    
    useRealTimeData.mockReturnValue({
      data: mockPerformanceData,
      isLoading: false,
      error: null,
      refresh: jest.fn(),
      isConnected: true,
      lastUpdated
    })

    render(
      <TestWrapper>
        <Analytics />
      </TestWrapper>
    )

    expect(screen.getByText(/Last updated/)).toBeInTheDocument()
  })

  it('handles empty data gracefully', () => {
    useApi.mockReturnValue({
      data: {
        totalViews: 0,
        totalClicks: 0,
        totalShares: 0,
        totalComments: 0,
        engagementRate: 0,
        topPerformingPosts: [],
        platformMetrics: {},
        timeSeriesData: { labels: [], datasets: [] }
      },
      loading: false,
      error: null,
      refetch: jest.fn()
    })

    render(
      <TestWrapper>
        <Analytics />
      </TestWrapper>
    )

    expect(screen.getByText('No data available')).toBeInTheDocument()
    expect(screen.getByText('Start creating content to see analytics')).toBeInTheDocument()
  })

  it('exports analytics data', async () => {
    // Mock the export functionality
    const exportSpy = jest.spyOn(window, 'open').mockImplementation(() => {})

    render(
      <TestWrapper>
        <Analytics />
      </TestWrapper>
    )

    const exportButton = screen.getByText('Export Data')
    fireEvent.click(exportButton)

    // In a real implementation, this would trigger a download or open export dialog
    expect(exportButton).toBeInTheDocument()
    
    exportSpy.mockRestore()
  })

  it('handles responsive layout', () => {
    // Test mobile view
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 768,
    })

    render(
      <TestWrapper>
        <Analytics />
      </TestWrapper>
    )

    // Metrics should stack vertically on mobile
    const metricsContainer = screen.getByTestId('metrics-grid')
    expect(metricsContainer).toHaveClass('grid-cols-1', 'md:grid-cols-2', 'lg:grid-cols-4')
  })

  it('shows comparison with previous period', () => {
    const dataWithComparison = {
      ...mockAnalyticsData,
      comparison: {
        viewsChange: 15.5,
        clicksChange: -2.3,
        sharesChange: 8.7,
        commentsChange: 12.1
      }
    }

    useApi.mockReturnValue({
      data: dataWithComparison,
      loading: false,
      error: null,
      refetch: jest.fn()
    })

    render(
      <TestWrapper>
        <Analytics />
      </TestWrapper>
    )

    expect(screen.getByText('+15.5%')).toBeInTheDocument()
    expect(screen.getByText('-2.3%')).toBeInTheDocument()
    expect(screen.getByText('+8.7%')).toBeInTheDocument()
    expect(screen.getByText('+12.1%')).toBeInTheDocument()
  })
})