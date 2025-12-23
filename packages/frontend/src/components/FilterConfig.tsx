import { useState } from 'react'
import api from '../api/client'
import type { ConnectionConfig, ColumnInfo, TableFilter } from '../types'

interface FilterConfigProps {
  connection: ConnectionConfig
  tables: string[]
  filters: TableFilter[]
  onChange: (filters: TableFilter[]) => void
}

export function FilterConfig({ connection, tables, filters, onChange }: FilterConfigProps) {
  const [expandedTable, setExpandedTable] = useState<string | null>(null)
  const [columns, setColumns] = useState<Record<string, ColumnInfo[]>>({})
  const [loadingColumns, setLoadingColumns] = useState<string | null>(null)

  const loadColumns = async (table: string) => {
    if (columns[table]) return

    setLoadingColumns(table)
    try {
      const response = await api.post<ColumnInfo[]>('/api/connections/columns', {
        connection,
        table,
      })
      setColumns((prev) => ({ ...prev, [table]: response.data }))
    } catch (error) {
      console.error('Failed to load columns:', error)
    } finally {
      setLoadingColumns(null)
    }
  }

  const handleToggleExpand = async (table: string) => {
    if (expandedTable === table) {
      setExpandedTable(null)
    } else {
      setExpandedTable(table)
      await loadColumns(table)
    }
  }

  const getFilter = (table: string): TableFilter => {
    return filters.find((f) => f.table_name === table) || { table_name: table }
  }

  const updateFilter = (table: string, updates: Partial<TableFilter>) => {
    const existing = filters.find((f) => f.table_name === table)
    if (existing) {
      onChange(
        filters.map((f) => (f.table_name === table ? { ...f, ...updates } : f))
      )
    } else {
      onChange([...filters, { table_name: table, ...updates }])
    }
  }

  const handleWhereChange = (table: string, where: string) => {
    updateFilter(table, { where_clause: where || undefined })
  }

  const handleColumnToggle = (table: string, column: string) => {
    const filter = getFilter(table)
    const currentColumns = filter.columns || []
    const newColumns = currentColumns.includes(column)
      ? currentColumns.filter((c) => c !== column)
      : [...currentColumns, column]
    updateFilter(table, { columns: newColumns.length > 0 ? newColumns : undefined })
  }

  if (tables.length === 0) {
    return null
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Filter Configuration</h3>
      <p className="text-sm text-gray-500 mb-4">
        Optionally configure WHERE clauses and column selection for each table
      </p>

      <div className="space-y-2">
        {tables.map((table) => {
          const filter = getFilter(table)
          const isExpanded = expandedTable === table
          const tableColumns = columns[table] || []

          return (
            <div key={table} className="border border-gray-200 rounded-lg">
              <button
                type="button"
                onClick={() => handleToggleExpand(table)}
                className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-50"
              >
                <span className="font-medium text-gray-700">{table}</span>
                <div className="flex items-center">
                  {(filter.where_clause || filter.columns) && (
                    <span className="mr-2 px-2 py-0.5 text-xs bg-indigo-100 text-indigo-700 rounded">
                      Filtered
                    </span>
                  )}
                  <svg
                    className={`w-5 h-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </button>

              {isExpanded && (
                <div className="px-4 pb-4 border-t border-gray-200">
                  <div className="mt-4">
                    <label className="block text-sm font-medium text-gray-700">WHERE Clause</label>
                    <input
                      type="text"
                      value={filter.where_clause || ''}
                      onChange={(e) => handleWhereChange(table, e.target.value)}
                      placeholder="e.g., created_at > '2024-01-01'"
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm"
                    />
                  </div>

                  <div className="mt-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Select Columns (leave empty for all)
                    </label>
                    {loadingColumns === table ? (
                      <p className="text-sm text-gray-500">Loading columns...</p>
                    ) : tableColumns.length > 0 ? (
                      <div className="max-h-40 overflow-y-auto grid grid-cols-2 gap-1">
                        {tableColumns.map((col) => (
                          <label key={col.name} className="flex items-center p-1 text-sm">
                            <input
                              type="checkbox"
                              checked={filter.columns?.includes(col.name) || false}
                              onChange={() => handleColumnToggle(table, col.name)}
                              className="h-3 w-3 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                            />
                            <span className="ml-2 text-gray-600">{col.name}</span>
                            <span className="ml-1 text-gray-400 text-xs">({col.type})</span>
                          </label>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-gray-500">No columns loaded</p>
                    )}
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
