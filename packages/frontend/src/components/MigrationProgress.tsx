import { useWebSocket } from '../hooks/useWebSocket'

interface MigrationProgressProps {
  migrationId: number
  onComplete?: () => void
}

export function MigrationProgress({ migrationId, onComplete }: MigrationProgressProps) {
  const { status, rowCount, errorMessage, isConnected } = useWebSocket(migrationId)

  const getStatusColor = () => {
    switch (status) {
      case 'completed':
        return 'bg-green-500'
      case 'running':
        return 'bg-blue-500'
      case 'failed':
        return 'bg-red-500'
      case 'cancelled':
        return 'bg-gray-500'
      default:
        return 'bg-yellow-500'
    }
  }

  const isFinished = ['completed', 'failed', 'cancelled'].includes(status)

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900">Migration Progress</h3>
        <div className="flex items-center">
          <div className={`w-2 h-2 rounded-full mr-2 ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-sm text-gray-500">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      <div className="space-y-4">
        {/* Status */}
        <div className="flex items-center">
          <span className="text-sm font-medium text-gray-700 w-24">Status:</span>
          <span className={`px-3 py-1 text-sm font-medium text-white rounded-full ${getStatusColor()}`}>
            {status.charAt(0).toUpperCase() + status.slice(1)}
          </span>
        </div>

        {/* Progress bar for running state */}
        {status === 'running' && (
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all duration-300 animate-pulse"
              style={{ width: '100%' }}
            />
          </div>
        )}

        {/* Row count */}
        <div className="flex items-center">
          <span className="text-sm font-medium text-gray-700 w-24">Rows:</span>
          <span className="text-lg font-bold text-gray-900">{rowCount.toLocaleString()}</span>
        </div>

        {/* Error message */}
        {errorMessage && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-700">{errorMessage}</p>
          </div>
        )}

        {/* Completion button */}
        {isFinished && onComplete && (
          <button
            onClick={onComplete}
            className="w-full mt-4 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
          >
            View History
          </button>
        )}
      </div>
    </div>
  )
}
