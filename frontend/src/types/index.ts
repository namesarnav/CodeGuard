export interface Location {
  file_path: string
  start_line: number
  end_line: number
  start_column?: number
  end_column?: number
  function_name?: string
}

export interface Issue {
  id: string
  type: 'vulnerability' | 'code_review' | 'auto_comment'
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info'
  title: string
  description: string
  location: Location
  rule_id?: string
  cwe_id?: string
  owasp_category?: string
  suggestion?: string
  code_snippet?: string
  fixed_code?: string
  metadata?: Record<string, any>
}

export interface ScanRequest {
  repository_url?: string
  repository_path?: string
  branch?: string
  file_paths?: string[]
  include_patterns?: string[]
  exclude_patterns?: string[]
}

export interface ScanResponse {
  scan_id: string
  status: 'pending' | 'in_progress' | 'completed' | 'failed'
  repository_url?: string
  repository_path?: string
  started_at: string
  completed_at?: string
  total_files: number
  scanned_files: number
  total_issues: number
  issues_by_severity: {
    critical: number
    high: number
    medium: number
    low: number
    info: number
  }
  error?: string
}

export interface ScanResult {
  scan_id: string
  status: 'pending' | 'in_progress' | 'completed' | 'failed'
  repository_url?: string
  repository_path?: string
  started_at: string
  completed_at?: string
  total_files: number
  scanned_files: number
  issues: Issue[]
  summary: {
    total_issues: number
    by_severity: {
      critical: number
      high: number
      medium: number
      low: number
      info: number
    }
    by_type: {
      vulnerability: number
      code_review: number
      auto_comment: number
    }
  }
}

