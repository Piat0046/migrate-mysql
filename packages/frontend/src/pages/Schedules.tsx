import { useState, useEffect } from 'react'
import api from '../api/client'
import type { Schedule, ConnectionConfig, TableFilter } from '../types'

const defaultConnection: ConnectionConfig = {
  host: 'localhost',
  port: 3306,
  user: '',
  password: '',
  database: '',
}

interface ScheduleFormData {
  name: string
  cron_expression: string
  source: ConnectionConfig
  tables?: string[]
  filters?: TableFilter[]
  is_active: boolean
}

export function Schedules() {
  const [schedules, setSchedules] = useState<Schedule[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [formData, setFormData] = useState<ScheduleFormData>({
    name: '',
    cron_expression: '',
    source: defaultConnection,
    is_active: true,
  })
  const [error, setError] = useState('')

  useEffect(() => {
    loadSchedules()
  }, [])

  const loadSchedules = async () => {
    setIsLoading(true)
    try {
      const response = await api.get<Schedule[]>('/api/schedules')
      setSchedules(response.data)
    } catch (error) {
      console.error('Failed to load schedules:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    try {
      const payload = {
        name: formData.name,
        cron_expression: formData.cron_expression,
        source_config: formData.source,
        tables: formData.tables,
        filters: formData.filters,
        is_active: formData.is_active,
      }

      if (editingId) {
        await api.put(`/api/schedules/${editingId}`, payload)
      } else {
        await api.post('/api/schedules', payload)
      }

      setShowForm(false)
      setEditingId(null)
      resetForm()
      loadSchedules()
    } catch (err) {
      setError('Failed to save schedule')
    }
  }

  const handleEdit = (schedule: Schedule) => {
    setFormData({
      name: schedule.name,
      cron_expression: schedule.cron_expression,
      source: schedule.source_config,
      tables: schedule.tables,
      filters: schedule.filters,
      is_active: schedule.is_active,
    })
    setEditingId(schedule.id)
    setShowForm(true)
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this schedule?')) return

    try {
      await api.delete(`/api/schedules/${id}`)
      loadSchedules()
    } catch (error) {
      console.error('Failed to delete schedule:', error)
    }
  }

  const handleToggleActive = async (schedule: Schedule) => {
    try {
      await api.put(`/api/schedules/${schedule.id}`, {
        ...schedule,
        source_config: schedule.source_config,
        is_active: !schedule.is_active,
      })
      loadSchedules()
    } catch (error) {
      console.error('Failed to toggle schedule:', error)
    }
  }

  const resetForm = () => {
    setFormData({
      name: '',
      cron_expression: '',
      source: defaultConnection,
      is_active: true,
    })
  }

  const formatNextRun = (dateString: string | null) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleString()
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Scheduled Migrations</h1>
        <button
          onClick={() => {
            resetForm()
            setEditingId(null)
            setShowForm(true)
          }}
          className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
        >
          New Schedule
        </button>
      </div>

      {/* Schedule Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">
                {editingId ? 'Edit Schedule' : 'New Schedule'}
              </h2>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Name</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Cron Expression
                  </label>
                  <input
                    type="text"
                    value={formData.cron_expression}
                    onChange={(e) => setFormData({ ...formData, cron_expression: e.target.value })}
                    placeholder="0 0 * * * (every day at midnight)"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    required
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    Format: minute hour day month weekday
                  </p>
                </div>

                <div className="border-t border-gray-200 pt-4">
                  <h3 className="text-sm font-medium text-gray-900 mb-3">Source Database</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Host</label>
                      <input
                        type="text"
                        value={formData.source.host}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            source: { ...formData.source, host: e.target.value },
                          })
                        }
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Port</label>
                      <input
                        type="number"
                        value={formData.source.port}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            source: { ...formData.source, port: parseInt(e.target.value) },
                          })
                        }
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">User</label>
                      <input
                        type="text"
                        value={formData.source.user}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            source: { ...formData.source, user: e.target.value },
                          })
                        }
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Password</label>
                      <input
                        type="password"
                        value={formData.source.password}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            source: { ...formData.source, password: e.target.value },
                          })
                        }
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                      />
                    </div>
                    <div className="col-span-2">
                      <label className="block text-sm font-medium text-gray-700">Database</label>
                      <input
                        type="text"
                        value={formData.source.database}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            source: { ...formData.source, database: e.target.value },
                          })
                        }
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                      />
                    </div>
                  </div>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="is_active"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                  />
                  <label htmlFor="is_active" className="ml-2 text-sm text-gray-700">
                    Active
                  </label>
                </div>

                {error && (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                    <p className="text-sm text-red-700">{error}</p>
                  </div>
                )}

                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowForm(false)}
                    className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
                  >
                    {editingId ? 'Update' : 'Create'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Schedules List */}
      {schedules.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <p className="text-gray-500 mb-4">No scheduled migrations</p>
          <button
            onClick={() => setShowForm(true)}
            className="text-indigo-600 hover:text-indigo-500 font-medium"
          >
            Create your first schedule
          </button>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Cron
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Database
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Next Run
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {schedules.map((schedule) => (
                <tr key={schedule.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {schedule.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono">
                    {schedule.cron_expression}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {schedule.source_config.host}:{schedule.source_config.port}/
                    {schedule.source_config.database}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <button
                      onClick={() => handleToggleActive(schedule)}
                      className={`px-2 py-1 text-xs font-medium rounded-full ${
                        schedule.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {schedule.is_active ? 'Active' : 'Inactive'}
                    </button>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatNextRun(schedule.next_run ?? null)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => handleEdit(schedule)}
                      className="text-indigo-600 hover:text-indigo-900 mr-4"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(schedule.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
