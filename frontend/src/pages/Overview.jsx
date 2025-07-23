import { useQuery } from '@tanstack/react-query'
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

const fetchMetrics = async () => {
  const response = await fetch('http://localhost:8000/api/metrics')
  if (!response.ok) throw new Error('Failed to fetch metrics')
  return response.json()
}

const fetchWorkflowStatus = async () => {
  const response = await fetch('http://localhost:8000/api/workflow/status')
  if (!response.ok) throw new Error('Failed to fetch workflow status')
  return response.json()
}

const fetchGoalsSummary = async () => {
  const response = await fetch('http://localhost:8000/api/goals/summary')
  if (!response.ok) throw new Error('Failed to fetch goals')
  return response.json()
}

const MetricCard = ({ title, value, change, changeType, icon: Icon, color = "blue" }) => {
  const colorClasses = {
    blue: 'text-blue-600',
    green: 'text-green-600',
    purple: 'text-purple-600',
    orange: 'text-orange-600'
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center">
        <Icon className={`h-8 w-8 ${colorClasses[color]}`} />
        <div className="ml-4">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <div className="flex items-center">
            <p className={`text-2xl font-bold ${colorClasses[color]}`}>{value}</p>
            <div className={`ml-2 flex items-center text-sm ${
              changeType === 'increase' ? 'text-green-600' : 'text-red-600'
            }`}>
              {changeType === 'increase' ? (
                <ArrowUpIcon className="h-4 w-4" />
              ) : (
                <ArrowDownIcon className="h-4 w-4" />
              )}
              <span>{change}</span>
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
    <div className="flex items-center justify-between p-4 bg-white rounded-lg shadow-sm">
      <div>
        <h3 className="font-medium text-gray-900">{stage.name}</h3>
        <p className="text-sm text-gray-500">
          {stage.status === 'running' 
            ? `Running... ${stage.progress}% complete`
            : stage.status === 'completed'
            ? `Completed in ${stage.duration_minutes}min`
            : `Scheduled for ${stage.scheduled_time}`
          }
        </p>
      </div>
      <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusColors[stage.status]}`}>
        {statusIcons[stage.status]} {stage.status}
      </span>
    </div>
  )
}

const GoalProgress = ({ goal }) => (
  <div className="mb-4">
    <div className="flex justify-between text-sm mb-1">
      <span className="font-medium text-gray-900">{goal.title}</span>
      <span className={goal.on_track ? 'text-green-600' : 'text-yellow-600'}>
        {Math.round(goal.progress)}%
      </span>
    </div>
    <div className="w-full bg-gray-200 rounded-full h-2">
      <div
        className={`h-2 rounded-full ${goal.on_track ? 'bg-green-500' : 'bg-yellow-500'}`}
        style={{ width: `${Math.min(goal.progress, 100)}%` }}
      />
    </div>
    <p className="text-xs text-gray-500 mt-1">{goal.current} → {goal.target}</p>
  </div>
)

export default function Overview() {
  const { data: metrics, isLoading: metricsLoading, error: metricsError } = useQuery({
    queryKey: ['metrics'],
    queryFn: fetchMetrics,
    refetchInterval: 5 * 60 * 1000,
  })

  const { data: workflow, isLoading: workflowLoading } = useQuery({
    queryKey: ['workflow'],
    queryFn: fetchWorkflowStatus,
    refetchInterval: 30 * 1000,
  })

  const { data: goals, isLoading: goalsLoading } = useQuery({
    queryKey: ['goals'],
    queryFn: fetchGoalsSummary,
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
              Autonomous content factory generating {metrics?.total_posts || 0} posts 
              with {metrics?.engagement_rate || 0}% avg engagement
            </p>
          </div>
          <div className="text-right">
            <div className="text-sm text-blue-100">Cycle #{workflow?.workflow?.cycle_count || 142}</div>
            <div className="text-lg font-semibold">
              {workflow?.workflow?.current_stage?.replace('_', ' ').toUpperCase() || 'ACTIVE'}
            </div>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Posts"
          value={metrics?.total_posts?.toLocaleString() || '0'}
          change="+12%"
          changeType="increase"
          icon={DocumentTextIcon}
          color="blue"
        />
        <MetricCard
          title="Engagement Rate"
          value={`${metrics?.engagement_rate || 0}%`}
          change="+0.8%"
          changeType="increase"
          icon={ChatBubbleLeftRightIcon}
          color="green"
        />
        <MetricCard
          title="Followers Gained"
          value={metrics?.followers_gained?.toLocaleString() || '0'}
          change="+23%"
          changeType="increase"
          icon={UsersIcon}
          color="purple"
        />
        <MetricCard
          title="Total Reach"
          value="26.8K"
          change="-2.1%"
          changeType="decrease"
          icon={EyeIcon}
          color="orange"
        />
      </div>

      {/* Workflow Status */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-900">🤖 Autonomous Workflow</h2>
          <button className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
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
        ) : (
          <div className="space-y-3">
            {workflow?.workflow?.stages?.map((stage, index) => (
              <WorkflowStage key={index} stage={stage} />
            ))}
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
          ) : (
            <div>
              {goals?.summary?.goals?.map((goal) => (
                <GoalProgress key={goal.id} goal={goal} />
              ))}
              <div className="text-sm text-gray-500 mt-4">
                {goals?.summary?.active_goals || 0} active goals • 
                {goals?.summary?.on_track_goals || 0} on track
              </div>
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">🧠 Memory System</h2>
          <div className="space-y-3">
            <div className="flex justify-between text-sm">
              <span>Content Items:</span>
              <span className="font-semibold">245</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>Research Articles:</span>
              <span className="font-semibold">45</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>Generated Posts:</span>
              <span className="font-semibold">156</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>Repurpose Ready:</span>
              <span className="font-semibold text-green-600">23</span>
            </div>
            <div className="pt-3 border-t">
              <div className="flex items-center text-sm text-blue-600 hover:text-blue-800 cursor-pointer">
                <ChartBarIcon className="h-4 w-4 mr-1" />
                View Memory Explorer →
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}