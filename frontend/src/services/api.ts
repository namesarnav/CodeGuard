import axios from 'axios'
import { ScanRequest, ScanResponse, ScanResult } from '../types'

const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

export const api = {
  async createScan(request: ScanRequest): Promise<ScanResponse> {
    const response = await apiClient.post<ScanResponse>('/scan', request)
    return response.data
  },

  async getScanResult(scanId: string): Promise<ScanResult> {
    const response = await apiClient.get<ScanResult>(`/scan/${scanId}`)
    return response.data
  },

  async getScans(): Promise<ScanResponse[]> {
    const response = await apiClient.get<ScanResponse[]>('/scans')
    return response.data
  },
}

