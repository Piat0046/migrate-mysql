import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import api from '../api/client'
import { ConnectionForm } from '../components/ConnectionForm'
import { TableSelector } from '../components/TableSelector'
import { FilterConfig } from '../components/FilterConfig'
import { MigrationProgress } from '../components/MigrationProgress'
import type { ConnectionConfig, TableFilter, MigrationResponse } from '../types'

const defaultConnection: ConnectionConfig = {
  host: 'localhost',
  port: 3306,
  user: '',
  password: '',
  database: '',
}

export function NewMigration() {
  const [searchParams] = useSearchParams()
  const isImport = searchParams.get('type') === 'import'
  const navigate = useNavigate()

  const [step, setStep] = useState(1)
  const [source, setSource] = useState<ConnectionConfig>(defaultConnection)
  const [target, setTarget] = useState<ConnectionConfig>(defaultConnection)
  const [tables, setTables] = useState<string[]>([])
  const [selectedTables, setSelectedTables] = useState<string[]>([])
  const [filters, setFilters] = useState<TableFilter[]>([])
  const [filePath, setFilePath] = useState('')
  const [migrationId, setMigrationId] = useState<number | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  const handleSourceTablesLoaded = (loadedTables: string[]) => {
    setTables(loadedTables)
    setSelectedTables(loadedTables)
  }

  const handleExport = async () => {
    setIsSubmitting(true)
    setError('')

    try {
      const response = await api.post<MigrationResponse>('/api/migrations/export', {
        source,
        tables: selectedTables.length > 0 ? selectedTables : undefined,
        filters: filters.filter((f) => f.where_clause || f.columns),
      })
      setMigrationId(response.data.id)
      setStep(4)
    } catch (err) {
      setError('Failed to start export')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleImport = async () => {
    setIsSubmitting(true)
    setError('')

    try {
      const response = await api.post<MigrationResponse>('/api/migrations/import', {
        target,
        file_path: filePath,
      })
      setMigrationId(response.data.id)
      setStep(4)
    } catch (err) {
      setError('Failed to start import')
    } finally {
      setIsSubmitting(false)
    }
  }

  const renderExportSteps = () => (
    <>
      {/* Step 1: Source Connection */}
      {step === 1 && (
        <div className="space-y-6">
          <ConnectionForm
            title="Source Database"
            value={source}
            onChange={setSource}
            onTablesLoaded={handleSourceTablesLoaded}
          />
          <div className="flex justify-end">
            <button
              onClick={() => setStep(2)}
              disabled={tables.length === 0}
              className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
            >
              Next: Select Tables
            </button>
          </div>
        </div>
      )}

      {/* Step 2: Table Selection */}
      {step === 2 && (
        <div className="space-y-6">
          <TableSelector
            tables={tables}
            selected={selectedTables}
            onChange={setSelectedTables}
          />
          <div className="flex justify-between">
            <button
              onClick={() => setStep(1)}
              className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
            >
              Back
            </button>
            <button
              onClick={() => setStep(3)}
              disabled={selectedTables.length === 0}
              className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
            >
              Next: Configure Filters
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Filter Configuration */}
      {step === 3 && (
        <div className="space-y-6">
          <FilterConfig
            connection={source}
            tables={selectedTables}
            filters={filters}
            onChange={setFilters}
          />

          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-700">{error}</p>
            </div>
          )}

          <div className="flex justify-between">
            <button
              onClick={() => setStep(2)}
              className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
            >
              Back
            </button>
            <button
              onClick={handleExport}
              disabled={isSubmitting}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
            >
              {isSubmitting ? 'Starting...' : 'Start Export'}
            </button>
          </div>
        </div>
      )}
    </>
  )

  const renderImportSteps = () => (
    <>
      {/* Step 1: Target Connection */}
      {step === 1 && (
        <div className="space-y-6">
          <ConnectionForm
            title="Target Database"
            value={target}
            onChange={setTarget}
          />
          <div className="flex justify-end">
            <button
              onClick={() => setStep(2)}
              className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
            >
              Next: Select File
            </button>
          </div>
        </div>
      )}

      {/* Step 2: File Selection */}
      {step === 2 && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">SQL File Path</h3>
            <input
              type="text"
              value={filePath}
              onChange={(e) => setFilePath(e.target.value)}
              placeholder="/path/to/dump.sql"
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            />
            <p className="mt-2 text-sm text-gray-500">
              Enter the path to the SQL file on the server
            </p>
          </div>

          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-700">{error}</p>
            </div>
          )}

          <div className="flex justify-between">
            <button
              onClick={() => setStep(1)}
              className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
            >
              Back
            </button>
            <button
              onClick={handleImport}
              disabled={isSubmitting || !filePath}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
            >
              {isSubmitting ? 'Starting...' : 'Start Import'}
            </button>
          </div>
        </div>
      )}
    </>
  )

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">
        {isImport ? 'Import Database' : 'Export Database'}
      </h1>

      {/* Progress indicator */}
      {step < 4 && (
        <div className="mb-8">
          <div className="flex items-center">
            {[1, 2, 3].slice(0, isImport ? 2 : 3).map((s, i) => (
              <div key={s} className="flex items-center">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center ${
                    step >= s ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-600'
                  }`}
                >
                  {s}
                </div>
                {i < (isImport ? 1 : 2) && (
                  <div
                    className={`w-16 h-1 ${step > s ? 'bg-indigo-600' : 'bg-gray-200'}`}
                  />
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Step content */}
      {step === 4 && migrationId ? (
        <MigrationProgress
          migrationId={migrationId}
          onComplete={() => navigate('/history')}
        />
      ) : isImport ? (
        renderImportSteps()
      ) : (
        renderExportSteps()
      )}
    </div>
  )
}
