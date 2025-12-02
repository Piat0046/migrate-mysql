import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/client'
import type { MigrationHistory, PaginatedResponse } from '../types'

export function Dashboard() {
  const [recentHistory, setRecentHistory] = useState<MigrationHistory[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await api.get<PaginatedResponse<MigrationHistory>>(
          '/api/history?page=1&page_size=5'
        )
        setRecentHistory(response.data.items)
      } catch (error) {
        console.error('Failed to fetch history:', error)
      } finally {
        setIsLoading(false)
      }
    }
    fetchHistory()
  }, [])

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      completed: 'bg-green-100 text-green-800',
      running: 'bg-blue-100 text-blue-800',
      pending: 'bg-yellow-100 text-yellow-800',
      failed: 'bg-red-100 text-red-800',
      cancelled: 'bg-gray-100 text-gray-800',
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <Link
          to="/migrations/new"
          className="p-6 bg-white rounded-lg shadow hover:shadow-md transition-shadow"
        >
          <div className="flex items-center">
            <div className="p-3 bg-indigo-100 rounded-lg">
              <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">New Export</h3>
              <p className="text-sm text-gray-500">Export database to SQL file</p>
            </div>
          </div>
        </Link>

        <Link
          to="/migrations/new?type=import"
          className="p-6 bg-white rounded-lg shadow hover:shadow-md transition-shadow"
        >
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-lg">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">New Import</h3>
              <p className="text-sm text-gray-500">Import SQL file to database</p>
            </div>
          </div>
        </Link>

        <Link
          to="/schedules"
          className="p-6 bg-white rounded-lg shadow hover:shadow-md transition-shadow"
        >
          <div className="flex items-center">
            <div className="p-3 bg-purple-100 rounded-lg">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">Schedules</h3>
              <p className="text-sm text-gray-500">Manage scheduled migrations</p>
            </div>
          </div>
        </Link>
      </div>

      {/* Recent History */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Recent Migrations</h2>
        </div>
        <div className="divide-y divide-gray-200">
          {isLoading ? (
            <div className="p-6 text-center text-gray-500">Loading...</div>
          ) : recentHistory.length === 0 ? (
            <div className="p-6 text-center text-gray-500">No migrations yet</div>
          ) : (
            recentHistory.map((item) => (
              <div key={item.id} className="px-6 py-4 flex items-center justify-between">
                <div>
                  <div className="flex items-center">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadge(item.status)}`}>
                      {item.status}
                    </span>
                    <span className="ml-2 text-sm font-medium text-gray-900">
                      {item.migration_type.toUpperCase()}
                    </span>
                  </div>
                  <p className="mt-1 text-sm text-gray-500">
                    {item.source_host}:{item.source_database}
                    {item.target_host && ` → ${item.target_host}:${item.target_database}`}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-900">{(item.row_count ?? 0).toLocaleString()} rows</p>
                  <p className="text-xs text-gray-500">
                    {new Date(item.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
            ))
          )}
        </div>
        {recentHistory.length > 0 && (
          <div className="px-6 py-4 border-t border-gray-200">
            <Link to="/history" className="text-sm text-indigo-600 hover:text-indigo-500">
              View all history →
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}
