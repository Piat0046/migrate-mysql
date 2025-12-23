import { useState } from 'react'
import api from '../api/client'
import type { ConnectionConfig, ConnectionTestResponse } from '../types'

interface ConnectionFormProps {
  title: string
  value: ConnectionConfig
  onChange: (config: ConnectionConfig) => void
  onTablesLoaded?: (tables: string[]) => void
}

export function ConnectionForm({ title, value, onChange, onTablesLoaded }: ConnectionFormProps) {
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null)
  const [isTesting, setIsTesting] = useState(false)

  const handleChange = (field: keyof ConnectionConfig, fieldValue: string | number) => {
    onChange({ ...value, [field]: fieldValue })
  }

  const handleTest = async () => {
    setIsTesting(true)
    setTestResult(null)

    try {
      const response = await api.post<ConnectionTestResponse>('/api/connections/test', value)
      setTestResult({
        success: response.data.success,
        message: response.data.message,
      })
      if (response.data.success && response.data.tables && onTablesLoaded) {
        onTablesLoaded(response.data.tables)
      }
    } catch (error) {
      setTestResult({
        success: false,
        message: 'Failed to test connection',
      })
    } finally {
      setIsTesting(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">{title}</h3>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Host</label>
          <input
            type="text"
            value={value.host}
            onChange={(e) => handleChange('host', e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            placeholder="localhost"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Port</label>
          <input
            type="number"
            value={value.port}
            onChange={(e) => handleChange('port', parseInt(e.target.value))}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">User</label>
          <input
            type="text"
            value={value.user}
            onChange={(e) => handleChange('user', e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            placeholder="root"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Password</label>
          <input
            type="password"
            value={value.password}
            onChange={(e) => handleChange('password', e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          />
        </div>
        <div className="col-span-2">
          <label className="block text-sm font-medium text-gray-700">Database</label>
          <input
            type="text"
            value={value.database}
            onChange={(e) => handleChange('database', e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            placeholder="mydb"
          />
        </div>
      </div>

      <div className="mt-4 flex items-center justify-between">
        <button
          type="button"
          onClick={handleTest}
          disabled={isTesting}
          className="px-4 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-md hover:bg-indigo-100 disabled:opacity-50"
        >
          {isTesting ? 'Testing...' : 'Test Connection'}
        </button>

        {testResult && (
          <span className={`text-sm ${testResult.success ? 'text-green-600' : 'text-red-600'}`}>
            {testResult.message}
          </span>
        )}
      </div>
    </div>
  )
}
