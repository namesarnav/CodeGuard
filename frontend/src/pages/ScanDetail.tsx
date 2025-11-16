import { useParams } from 'react-router-dom'
import { useQuery } from 'react-query'
import Editor from '@monaco-editor/react'
import { api } from '../services/api'
import { ScanResult, Issue } from '../types'
import { AlertTriangle, Info, CheckCircle, XCircle } from 'lucide-react'

export default function ScanDetail() {
  const { scanId } = useParams<{ scanId: string }>()
  const { data: scan, isLoading } = useQuery<ScanResult>(
    ['scan', scanId],
    () => api.getScanResult(scanId!),
    { enabled: !!scanId, refetchInterval: 5000 }
  )

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'low':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
      case 'high':
        return <AlertTriangle className="h-5 w-5" />
      case 'medium':
        return <Info className="h-5 w-5" />
      default:
        return <CheckCircle className="h-5 w-5" />
    }
  }

  if (isLoading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!scan) {
    return <div>Scan not found</div>
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Scan Results</h1>
        <p className="mt-2 text-gray-600">Scan ID: {scan.scan_id}</p>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-2xl font-bold text-gray-900">{scan.total_issues}</div>
          <div className="text-sm text-gray-500">Total Issues</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-2xl font-bold text-red-600">
            {scan.summary?.by_severity?.critical || 0}
          </div>
          <div className="text-sm text-gray-500">Critical</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-2xl font-bold text-orange-600">
            {scan.summary?.by_severity?.high || 0}
          </div>
          <div className="text-sm text-gray-500">High</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-2xl font-bold text-gray-900">
            {scan.scanned_files} / {scan.total_files}
          </div>
          <div className="text-sm text-gray-500">Files Scanned</div>
        </div>
      </div>

      {/* Issues List */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Issues</h2>
        </div>
        <div className="divide-y divide-gray-200">
          {scan.issues.map((issue: Issue) => (
            <div key={issue.id} className="p-6 hover:bg-gray-50">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-medium border ${getSeverityColor(issue.severity)}`}>
                      {getSeverityIcon(issue.severity)}
                      <span>{issue.severity}</span>
                    </span>
                    <span className="text-xs text-gray-500">{issue.type}</span>
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">{issue.title}</h3>
                  <p className="text-sm text-gray-600 mb-2">{issue.description}</p>
                  <p className="text-xs text-gray-500 font-mono">
                    {issue.location.file_path}:{issue.location.start_line}-{issue.location.end_line}
                  </p>
                  {issue.suggestion && (
                    <div className="mt-3 p-3 bg-blue-50 rounded-md">
                      <p className="text-sm font-medium text-blue-900">Suggestion:</p>
                      <p className="text-sm text-blue-800">{issue.suggestion}</p>
                    </div>
                  )}
                  {issue.code_snippet && (
                    <div className="mt-3">
                      <Editor
                        height="200px"
                        defaultLanguage={issue.location.file_path.split('.').pop()}
                        value={issue.code_snippet}
                        options={{
                          readOnly: true,
                          minimap: { enabled: false },
                          fontSize: 12,
                        }}
                      />
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

