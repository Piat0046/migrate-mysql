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

  const getStatusConfig = (status: string) => {
    const configs: Record<string, { bg: string; text: string; dot: string }> = {
      completed: { bg: 'bg-emerald-50', text: 'text-emerald-700', dot: 'bg-emerald-500' },
      running: { bg: 'bg-blue-50', text: 'text-blue-700', dot: 'bg-blue-500 animate-pulse' },
      pending: { bg: 'bg-amber-50', text: 'text-amber-700', dot: 'bg-amber-500' },
      failed: { bg: 'bg-red-50', text: 'text-red-700', dot: 'bg-red-500' },
      cancelled: { bg: 'bg-slate-100', text: 'text-slate-600', dot: 'bg-slate-400' },
    }
    return configs[status] || { bg: 'bg-slate-100', text: 'text-slate-600', dot: 'bg-slate-400' }
  }

  const quickActions = [
    {
      to: '/new',
      title: 'New Export',
      description: 'Export database to SQL file',
      icon: 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12',
      gradient: 'from-indigo-500 to-purple-600',
      shadow: 'shadow-indigo-500/25',
    },
    {
      to: '/new?type=import',
      title: 'New Import',
      description: 'Import SQL file to database',
      icon: 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4',
      gradient: 'from-emerald-500 to-teal-600',
      shadow: 'shadow-emerald-500/25',
    },
    {
      to: '/schedules',
      title: 'Schedules',
      description: 'Manage scheduled migrations',
      icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z',
      gradient: 'from-violet-500 to-purple-600',
      shadow: 'shadow-violet-500/25',
    },
  ]

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
        <p className="mt-1 text-slate-500">Welcome back! Here's what's happening with your migrations.</p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {quickActions.map((action) => (
          <Link
            key={action.to}
            to={action.to}
            className="group relative bg-white rounded-2xl border border-slate-200 p-6 hover:border-slate-300 hover:shadow-lg transition-all duration-300"
          >
            <div className="flex items-start justify-between">
              <div className={`w-12 h-12 bg-gradient-to-br ${action.gradient} rounded-xl flex items-center justify-center shadow-lg ${action.shadow}`}>
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={action.icon} />
                </svg>
              </div>
              <svg className="w-5 h-5 text-slate-300 group-hover:text-slate-500 group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </div>
            <div className="mt-4">
              <h3 className="text-lg font-semibold text-slate-900 group-hover:text-indigo-600 transition-colors">{action.title}</h3>
              <p className="mt-1 text-sm text-slate-500">{action.description}</p>
            </div>
          </Link>
        ))}
      </div>

      {/* Recent History */}
      <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden">
        <div className="px-6 py-5 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">Recent Migrations</h2>
            <p className="text-sm text-slate-500">Your latest database operations</p>
          </div>
          {recentHistory.length > 0 && (
            <Link
              to="/history"
              className="text-sm font-medium text-indigo-600 hover:text-indigo-700 flex items-center gap-1"
            >
              View all
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </Link>
          )}
        </div>

        <div className="divide-y divide-slate-100">
          {isLoading ? (
            <div className="p-12 text-center">
              <div className="inline-flex items-center justify-center w-12 h-12 bg-slate-100 rounded-xl mb-4">
                <svg className="w-6 h-6 text-slate-400 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </div>
              <p className="text-slate-500">Loading migrations...</p>
            </div>
          ) : recentHistory.length === 0 ? (
            <div className="p-12 text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-slate-100 rounded-2xl mb-4">
                <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-slate-900 mb-1">No migrations yet</h3>
              <p className="text-slate-500 mb-4">Get started by creating your first migration</p>
              <Link
                to="/new"
                className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors"
              >
                Create Migration
              </Link>
            </div>
          ) : (
            recentHistory.map((item) => {
              const statusConfig = getStatusConfig(item.status)
              return (
                <div key={item.id} className="px-6 py-4 hover:bg-slate-50 transition-colors">
                  <div className="flex items-center justify-between gap-4">
                    <div className="flex items-center gap-4 min-w-0">
                      {/* Type indicator */}
                      <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
                        item.migration_type === 'export'
                          ? 'bg-indigo-100 text-indigo-600'
                          : 'bg-emerald-100 text-emerald-600'
                      }`}>
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={
                            item.migration_type === 'export'
                              ? 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12'
                              : 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4'
                          } />
                        </svg>
                      </div>

                      <div className="min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded-lg ${statusConfig.bg} ${statusConfig.text}`}>
                            <span className={`w-1.5 h-1.5 rounded-full ${statusConfig.dot}`}></span>
                            {item.status.charAt(0).toUpperCase() + item.status.slice(1)}
                          </span>
                          <span className="text-xs text-slate-400 uppercase tracking-wide font-medium">
                            {item.migration_type}
                          </span>
                        </div>
                        <p className="mt-1 text-sm text-slate-600 truncate">
                          <span className="font-medium">{item.source_database}</span>
                          <span className="text-slate-400"> @ {item.source_host}</span>
                          {item.target_host && (
                            <>
                              <span className="text-slate-300 mx-2">→</span>
                              <span className="font-medium">{item.target_database}</span>
                              <span className="text-slate-400"> @ {item.target_host}</span>
                            </>
                          )}
                        </p>
                      </div>
                    </div>

                    <div className="text-right flex-shrink-0">
                      <p className="text-sm font-semibold text-slate-900">{(item.row_count ?? 0).toLocaleString()} rows</p>
                      <p className="text-xs text-slate-400 mt-0.5">
                        {new Date(item.created_at).toLocaleDateString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </p>
                    </div>
                  </div>
                </div>
              )
            })
          )}
        </div>
      </div>
    </div>
  )
}
