import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from 'react-query'
import { api } from '../services/api'
import { ScanRequest } from '../types'

export default function NewScan() {
  const navigate = useNavigate()
  const [repositoryUrl, setRepositoryUrl] = useState('')
  const [repositoryPath, setRepositoryPath] = useState('')
  const [branch, setBranch] = useState('')

  const mutation = useMutation(
    (data: ScanRequest) => api.createScan(data),
    {
      onSuccess: (data) => {
        navigate(`/scan/${data.scan_id}`)
      },
    }
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate({
      repository_url: repositoryUrl || undefined,
      repository_path: repositoryPath || undefined,
      branch: branch || undefined,
    })
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">New Scan</h1>
        <p className="mt-2 text-gray-600">Scan a repository for vulnerabilities and code issues</p>
      </div>

      <form onSubmit={handleSubmit} className="bg-white shadow rounded-lg p-6">
        <div className="space-y-6">
          <div>
            <label htmlFor="repositoryUrl" className="block text-sm font-medium text-gray-700">
              GitHub Repository URL
            </label>
            <input
              type="url"
              id="repositoryUrl"
              value={repositoryUrl}
              onChange={(e) => setRepositoryUrl(e.target.value)}
              placeholder="https://github.com/user/repo"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            />
            <p className="mt-1 text-sm text-gray-500">Or provide a local path below</p>
          </div>

          <div>
            <label htmlFor="repositoryPath" className="block text-sm font-medium text-gray-700">
              Local Repository Path
            </label>
            <input
              type="text"
              id="repositoryPath"
              value={repositoryPath}
              onChange={(e) => setRepositoryPath(e.target.value)}
              placeholder="/path/to/repository"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            />
          </div>

          <div>
            <label htmlFor="branch" className="block text-sm font-medium text-gray-700">
              Branch (optional)
            </label>
            <input
              type="text"
              id="branch"
              value={branch}
              onChange={(e) => setBranch(e.target.value)}
              placeholder="main"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            />
          </div>

          {mutation.isError && (
            <div className="rounded-md bg-red-50 p-4">
              <p className="text-sm text-red-800">
                Error: {mutation.error instanceof Error ? mutation.error.message : 'Unknown error'}
              </p>
            </div>
          )}

          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={() => navigate('/')}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={mutation.isLoading || (!repositoryUrl && !repositoryPath)}
              className="px-4 py-2 bg-primary-600 text-white rounded-md text-sm font-medium hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {mutation.isLoading ? 'Starting Scan...' : 'Start Scan'}
            </button>
          </div>
        </div>
      </form>
    </div>
  )
}

