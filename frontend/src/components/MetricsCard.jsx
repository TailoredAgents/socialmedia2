import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/24/solid'

export default function MetricsCard({ stat }) {
  return (
    <div className="bg-white overflow-hidden shadow rounded-lg">
      <div className="p-5">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <stat.icon className="h-6 w-6 text-gray-400" />
          </div>
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-gray-500 truncate">
                {stat.name}
              </dt>
              <dd className="flex items-baseline">
                <div className="text-2xl font-semibold text-gray-900">
                  {stat.value}
                </div>
                <div className={`ml-2 flex items-baseline text-sm font-semibold ${
                  stat.changeType === 'increase' ? 'text-green-600' : 'text-red-600'
                }`}>
                  {stat.changeType === 'increase' ? (
                    <ArrowUpIcon className="h-3 w-3 flex-shrink-0 self-center text-green-500" />
                  ) : (
                    <ArrowDownIcon className="h-3 w-3 flex-shrink-0 self-center text-red-500" />
                  )}
                  <span className="sr-only">
                    {stat.changeType === 'increase' ? 'Increased' : 'Decreased'} by
                  </span>
                  {stat.change}
                </div>
              </dd>
            </dl>
          </div>
        </div>
      </div>
    </div>
  )
}