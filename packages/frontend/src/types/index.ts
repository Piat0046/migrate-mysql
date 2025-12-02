// Auth types
export interface User {
  id: number
  username: string
  is_active: boolean
  created_at: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface Token {
  access_token: string
  token_type: string
}

// Connection types
export interface ConnectionConfig {
  host: string
  port: number
  user: string
  password: string
  database: string
}

export interface ConnectionTestResponse {
  success: boolean
  message: string
  tables?: string[]
}

export interface ColumnInfo {
  name: string
  type: string
  nullable: boolean
  key?: string
  default?: string
}

// Filter types
export interface TableFilter {
  table_name: string
  where_clause?: string
  columns?: string[]
}

// Migration types
export interface ExportRequest {
  source: ConnectionConfig
  tables?: string[]
  filters?: TableFilter[]
}

export interface ImportRequest {
  target: ConnectionConfig
  file_path: string
}

export interface MigrationResponse {
  id: number
  status: string
  message: string
}

export interface MigrationStatus {
  id: number
  type: string
  status: string
  row_count: number
  error_message?: string
  started_at?: string
  completed_at?: string
}

export interface MigrationHistory {
  id: number
  migration_type: string
  source_host: string
  source_port: number
  source_database: string
  target_host?: string
  target_port?: number
  target_database?: string
  tables?: string[]
  filters?: TableFilter[]
  file_path?: string
  status: string
  row_count?: number
  error_message?: string
  started_at: string
  completed_at?: string
  created_at: string
}

// Schedule types
export interface Schedule {
  id: number
  name: string
  cron_expression: string
  source_config: ConnectionConfig
  tables?: string[]
  filters?: TableFilter[]
  is_active: boolean
  last_run?: string
  next_run?: string
  created_at: string
}

export interface ScheduleCreate {
  name: string
  cron_expression: string
  source_config: ConnectionConfig
  tables?: string[]
  filters?: TableFilter[]
  is_active?: boolean
}

// Pagination
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  pages: number
}

// WebSocket message types
export interface WSStatusMessage {
  type: 'status' | 'progress'
  migration_id: number
  status: string
  row_count: number
  error_message?: string
  started_at?: string
  completed_at?: string
}
