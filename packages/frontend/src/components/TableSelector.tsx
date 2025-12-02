interface TableSelectorProps {
  tables: string[]
  selected: string[]
  onChange: (selected: string[]) => void
}

export function TableSelector({ tables, selected, onChange }: TableSelectorProps) {
  const handleToggle = (table: string) => {
    if (selected.includes(table)) {
      onChange(selected.filter((t) => t !== table))
    } else {
      onChange([...selected, table])
    }
  }

  const handleSelectAll = () => {
    if (selected.length === tables.length) {
      onChange([])
    } else {
      onChange([...tables])
    }
  }

  if (tables.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Select Tables</h3>
        <p className="text-gray-500">Test connection first to load tables</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900">Select Tables</h3>
        <button
          type="button"
          onClick={handleSelectAll}
          className="text-sm text-indigo-600 hover:text-indigo-500"
        >
          {selected.length === tables.length ? 'Deselect All' : 'Select All'}
        </button>
      </div>

      <div className="max-h-64 overflow-y-auto space-y-2">
        {tables.map((table) => (
          <label key={table} className="flex items-center p-2 rounded hover:bg-gray-50 cursor-pointer">
            <input
              type="checkbox"
              checked={selected.includes(table)}
              onChange={() => handleToggle(table)}
              className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            />
            <span className="ml-3 text-sm text-gray-700">{table}</span>
          </label>
        ))}
      </div>

      <p className="mt-4 text-sm text-gray-500">
        {selected.length} of {tables.length} tables selected
      </p>
    </div>
  )
}
