import { useQuery } from '@tanstack/react-query'
import { ApiErrorBoundary } from '../components/ErrorBoundary'
import { 
  ArrowUpIcon, 
  ArrowDownIcon,
  DocumentTextIcon,
  ChatBubbleLeftRightIcon,
  UsersIcon,
  EyeIcon,
  PlayIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline'
import { useEnhancedApi } from '../hooks/useEnhancedApi'
import { useRealTimeMetrics } from '../hooks/useRealTimeData'

const MetricCard = ({ title, value, change, changeType, icon: Icon, color = "blue" }) => {
  const colorClasses = {
    blue: 'text-blue-600',
    green: 'text-green-600',
    purple: 'text-purple-600',
    orange: 'text-orange-600'
  }

  return (
    <div className="bg-white rounded-lg shadow p-6" role="article" aria-labelledby={`metric-${title.replace(/\s+/g, '-').toLowerCase()}`}>
      <div className="flex items-center">
        <Icon className={`h-8 w-8 ${colorClasses[color]}`} aria-hidden="true" />
        <div className="ml-4">
          <p id={`metric-${title.replace(/\s+/g, '-').toLowerCase()}`} className="text-sm font-medium text-gray-600">{title}</p>
          <div className="flex items-center">
            <p className={`text-2xl font-bold ${colorClasses[color]}`} aria-label={`${title}: ${value}`}>{value}</p>
            <div className={`ml-2 flex items-center text-sm ${
              changeType === 'increase' ? 'text-green-600' : 'text-red-600'
            }`}>
              {changeType === 'increase' ? (
                <ArrowUpIcon className="h-4 w-4" aria-hidden="true" />
              ) : (
                <ArrowDownIcon className="h-4 w-4" aria-hidden="true" />
              )}
              <span aria-label={`Change: ${changeType === 'increase' ? 'increased' : 'decreased'} by ${change}`}>{change}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

const WorkflowStage = ({ stage }) => {
  const statusColors = {
    completed: 'bg-green-100 text-green-800',
    running: 'bg-blue-100 text-blue-800',
    pending: 'bg-gray-100 text-gray-800'
  }

  const statusIcons = {
    completed: '✓',
    running: '🔄',
    pending: '⏳'
  }

  return (
    <div className="flex items-center justify-between p-4 bg-white rounded-lg shadow-sm" role="article" aria-labelledby={`stage-${stage.name.replace(/\s+/g, '-').toLowerCase()}`}>
      <div>
        <h3 id={`stage-${stage.name.replace(/\s+/g, '-').toLowerCase()}`} className="font-medium text-gray-900">{stage.name}</h3>
        <p className="text-sm text-gray-500" aria-live="polite">
          {stage.status === 'running' 
            ? `Running... ${stage.progress}% complete`
            : stage.status === 'completed'
            ? `Completed in ${stage.duration_minutes}min`
            : `Scheduled for ${stage.scheduled_time}`
          }
        </p>
      </div>
      <span 
        className={`px-3 py-1 rounded-full text-sm font-medium ${statusColors[stage.status]}`}
        role="status"
        aria-label={`Status: ${stage.status}`}
      >
        <span aria-hidden="true">{statusIcons[stage.status]}</span> {stage.status}
      </span>
    </div>
  )
}

const GoalProgress = ({ goal }) => (
  <div className="mb-4" role="article" aria-labelledby={`goal-${goal.title.replace(/\s+/g, '-').toLowerCase()}`}>
    <div className="flex justify-between text-sm mb-1">
      <span id={`goal-${goal.title.replace(/\s+/g, '-').toLowerCase()}`} className="font-medium text-gray-900">{goal.title}</span>
      <span className={goal.on_track ? 'text-green-600' : 'text-yellow-600'} aria-label={`Progress: ${Math.round(goal.progress)} percent`}>
        {Math.round(goal.progress)}%
      </span>
    </div>
    <div className="w-full bg-gray-200 rounded-full h-2" role="progressbar" aria-valuenow={goal.progress} aria-valuemin="0" aria-valuemax="100" aria-labelledby={`goal-${goal.title.replace(/\s+/g, '-').toLowerCase()}`}>
      <div
        className={`h-2 rounded-full ${goal.on_track ? 'bg-green-500' : 'bg-yellow-500'}`}
        style={{ width: `${Math.min(goal.progress, 100)}%` }}
      />
    </div>
    <p className="text-xs text-gray-500 mt-1" aria-label={`Current: ${goal.current}, Target: ${goal.target}`}>{goal.current} → {goal.target}</p>
  </div>
)

export default function Overview() {
  const { api } = useEnhancedApi()
  const { metrics: realTimeMetrics, connectionStatus } = useRealTimeMetrics()
  
  const { data: metrics, isLoading: metricsLoading, error: metricsError } = useQuery({
    queryKey: ['metrics'],
    queryFn: () => api.analytics.getMetrics(),
    refetchInterval: 5 * 60 * 1000,
    retry: 2
  })

  const { data: workflow, isLoading: workflowLoading } = useQuery({
    queryKey: ['workflow-status'],
    queryFn: () => api.workflow.getStatusSummary(),
    refetchInterval: 30 * 1000,
    retry: 2
  })

  const { data: goals, isLoading: goalsLoading } = useQuery({
    queryKey: ['goals-summary'],
    queryFn: () => api.goals.getDashboard(),
    retry: 2
  })

  const { data: memoryStats, isLoading: memoryLoading } = useQuery({
    queryKey: ['memory-analytics'],
    queryFn: () => api.memory.getAnalytics(),
    refetchInterval: 5 * 60 * 1000,
    retry: 2
  })

  if (metricsLoading) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="h-24 bg-gray-300 rounded-lg"></div>
        <div className="grid grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-32 bg-gray-300 rounded-lg"></div>
          ))}
        </div>
      </div>
    )
  }

  if (metricsError) {
    return (
      <div className="rounded-md bg-red-50 p-4">
        <div className="text-sm text-red-800">
          Failed to load dashboard data. Make sure the backend is running on http://localhost:8000
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg shadow-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">🚀 AI Social Media Content Agent</h1>
            <p className="text-blue-100">
              Autonomous content factory generating {realTimeMetrics?.postsToday || metrics?.total_posts || 0} posts 
              with {realTimeMetrics?.engagementRate || metrics?.engagement_rate || 0}% avg engagement
            </p>
          </div>
          <div className="text-right">
            <div className="text-sm text-blue-100">
              Connection: {connectionStatus} • {realTimeMetrics?.activeUsers || 0} active users
            </div>
            <div className="text-lg font-semibold">
              {workflow?.current_stage?.replace('_', ' ').toUpperCase() || 'ACTIVE'}
            </div>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Views"
          value={realTimeMetrics?.totalViews?.toLocaleString() || metrics?.total_views?.toLocaleString() || '0'}
          change={`${realTimeMetrics?.viewsChange || '+12'}%`}
          changeType={realTimeMetrics?.viewsChange >= 0 ? "increase" : "decrease"}
          icon={EyeIcon}
          color="blue"
        />
        <MetricCard
          title="Engagement Rate"
          value={`${realTimeMetrics?.engagementRate || metrics?.engagement_rate || 0}%`}
          change={`${realTimeMetrics?.engagementRateChange || '+0.8'}%`}
          changeType={realTimeMetrics?.engagementRateChange >= 0 ? "increase" : "decrease"}
          icon={ChatBubbleLeftRightIcon}
          color="green"
        />
        <MetricCard
          title="Total Followers"
          value={realTimeMetrics?.totalFollowers?.toLocaleString() || metrics?.total_followers?.toLocaleString() || '0'}
          change={`${realTimeMetrics?.followersChange || '+23'}%`}
          changeType={realTimeMetrics?.followersChange >= 0 ? "increase" : "decrease"}
          icon={UsersIcon}
          color="purple"
        />
        <MetricCard
          title="Total Engagement"
          value={realTimeMetrics?.totalEngagement?.toLocaleString() || metrics?.total_engagement?.toLocaleString() || '0'}
          change={`${realTimeMetrics?.engagementChange || '+5.2'}%`}
          changeType={realTimeMetrics?.engagementChange >= 0 ? "increase" : "decrease"}
          icon={DocumentTextIcon}
          color="orange"
        />
      </div>

      {/* Workflow Status */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-900">🤖 Autonomous Workflow</h2>
          <button 
            onClick={() => api.workflow.executeDailyWorkflow()}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            <PlayIcon className="h-4 w-4 mr-2" />
            Trigger Cycle
          </button>
        </div>
        
        {workflowLoading ? (
          <div className="animate-pulse space-y-3">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-16 bg-gray-200 rounded-lg"></div>
            ))}
          </div>
        ) : workflow?.executions?.length > 0 ? (
          <div className="space-y-3">
            {workflow.executions.slice(0, 4).map((execution, index) => (
              <WorkflowStage key={index} stage={{
                name: execution.workflow_type,
                status: execution.status,
                progress: execution.progress || 0,
                duration_minutes: execution.duration_minutes,
                scheduled_time: execution.started_at
              }} />
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <PlayIcon className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p>No recent workflow executions</p>
            <p className="text-sm">Click "Trigger Cycle" to start a new workflow</p>
          </div>
        )}
      </div>

      {/* Goals & Memory */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">🎯 Goal Progress</h2>
          {goalsLoading ? (
            <div className="animate-pulse space-y-4">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="space-y-2">
                  <div className="h-4 bg-gray-200 rounded"></div>
                  <div className="h-2 bg-gray-200 rounded"></div>
                </div>
              ))}
            </div>
          ) : goals?.goals?.length > 0 ? (
            <div>
              {goals.goals.slice(0, 3).map((goal) => (
                <GoalProgress key={goal.id} goal={{
                  title: goal.title,
                  progress: goal.progress_percentage,
                  current: goal.current_value,
                  target: goal.target_value,
                  on_track: goal.is_on_track
                }} />
              ))}
              <div className="text-sm text-gray-500 mt-4">
                {goals?.active_goals || 0} active goals • 
                {goals?.on_track_goals || 0} on track
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <ChartBarIcon className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>No goals yet</p>
              <p className="text-sm">Create your first goal to start tracking progress</p>
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">🧠 Memory System</h2>
          {memoryLoading ? (
            <div className="animate-pulse space-y-3">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="flex justify-between">
                  <div className="h-4 bg-gray-200 rounded w-24"></div>
                  <div className="h-4 bg-gray-200 rounded w-8"></div>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span>Content Items:</span>
                <span className="font-semibold">{memoryStats?.total_content || 0}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Vector Embeddings:</span>
                <span className="font-semibold">{memoryStats?.total_embeddings || 0}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>High Performing:</span>
                <span className="font-semibold text-green-600">{memoryStats?.high_performing || 0}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Repurpose Ready:</span>
                <span className="font-semibold text-blue-600">{memoryStats?.repurpose_candidates || 0}</span>
              </div>
              <div className="pt-3 border-t">
                <a href="/memory" className="flex items-center text-sm text-blue-600 hover:text-blue-800 cursor-pointer">
                  <ChartBarIcon className="h-4 w-4 mr-1" />
                  View Memory Explorer →
                </a>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}