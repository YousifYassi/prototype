import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, useNavigate } from 'react-router-dom'
import { toast } from 'react-toastify'
import { projectApi } from '../lib/api'
import { 
  ArrowLeft, Settings, FileText, Camera, FileVideo, 
  Trash2, AlertTriangle, Shield, ExternalLink 
} from 'lucide-react'

export default function ProjectDetailsPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<'overview' | 'regulations' | 'settings'>('overview')
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)

  const { data: project, isLoading, error } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => projectApi.get(parseInt(projectId!)),
    enabled: !!projectId,
  })

  const deleteMutation = useMutation({
    mutationFn: () => projectApi.delete(parseInt(projectId!)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      toast.success('Project deleted successfully')
      navigate('/projects')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete project')
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading project...</p>
        </div>
      </div>
    )
  }

  if (error || !project) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">Error loading project. Please try again.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <button
          onClick={() => navigate('/projects')}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Projects
        </button>
        
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{project.name}</h1>
            <div className="flex items-center space-x-4 mt-2 text-sm text-gray-600">
              <span className="flex items-center">
                <Shield className="h-4 w-4 mr-1" />
                {project.jurisdiction.name}
              </span>
              <span>•</span>
              <span>{project.industry.name}</span>
            </div>
          </div>
          
          <button
            onClick={() => setShowDeleteConfirm(true)}
            className="btn-secondary text-red-600 hover:bg-red-50 flex items-center"
          >
            <Trash2 className="h-4 w-4 mr-2" />
            Delete Project
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('overview')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'overview'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('regulations')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'regulations'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <FileText className="h-4 w-4 inline mr-2" />
            Regulations
          </button>
          <button
            onClick={() => setActiveTab('settings')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'settings'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <Settings className="h-4 w-4 inline mr-2" />
            Settings
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Info Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Minimum Severity</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">
                    {getSeverityLabel(project.min_severity_alert)}
                  </p>
                </div>
                <AlertTriangle className="h-8 w-8 text-orange-500" />
              </div>
            </div>

            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Active Cameras</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">0</p>
                </div>
                <Camera className="h-8 w-8 text-blue-500" />
              </div>
            </div>

            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Videos Processed</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">0</p>
                </div>
                <FileVideo className="h-8 w-8 text-green-500" />
              </div>
            </div>
          </div>

          {/* Action Severities */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Action Severity Levels</h3>
            {project.action_severities && project.action_severities.length > 0 ? (
              <div className="space-y-2">
                {project.action_severities.map((action: any) => (
                  <div
                    key={action.action_name}
                    className="flex items-center justify-between py-3 px-4 bg-gray-50 rounded-lg"
                  >
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">
                        {action.action_name.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}
                      </p>
                      {action.description && (
                        <p className="text-sm text-gray-600 mt-1">{action.description}</p>
                      )}
                    </div>
                    <div className="flex items-center space-x-3">
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${getSeverityColor(action.severity_level)}`}>
                        {getSeverityLabel(action.severity_level)}
                      </span>
                      {action.is_custom && (
                        <span className="text-xs text-blue-600 font-medium">Custom</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-600 text-center py-8">
                No severity levels configured for this jurisdiction and industry combination.
              </p>
            )}
          </div>
        </div>
      )}

      {activeTab === 'regulations' && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Applicable Regulations</h3>
          
          {project.jurisdiction.regulation_url && (
            <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-800 mb-2">
                <strong>Jurisdiction:</strong> {project.jurisdiction.name}
              </p>
              <a
                href={project.jurisdiction.regulation_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-blue-600 hover:text-blue-800 flex items-center"
              >
                View Official Regulations
                <ExternalLink className="h-3 w-3 ml-1" />
              </a>
            </div>
          )}

          <p className="text-gray-600">
            Regulations are loaded from the {project.jurisdiction.name} jurisdiction for 
            {' '}{project.industry.name.toLowerCase()} operations.
          </p>
          
          <div className="mt-6">
            <p className="text-sm text-gray-500 italic">
              Detailed regulation mapping is configured in the backend and applied during 
              safety monitoring. Custom severity levels can be adjusted in the Settings tab.
            </p>
          </div>
        </div>
      )}

      {activeTab === 'settings' && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Project Settings</h3>
          <p className="text-gray-600 mb-6">
            Advanced project settings and customization options coming soon.
          </p>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Project Name
              </label>
              <p className="text-gray-900">{project.name}</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Minimum Alert Severity
              </label>
              <p className="text-gray-900">{getSeverityLabel(project.min_severity_alert)}</p>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Delete Project?</h3>
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete "{project.name}"? This action cannot be undone.
              All associated cameras and videos will remain but will no longer be linked to this project.
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  deleteMutation.mutate()
                  setShowDeleteConfirm(false)
                }}
                className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
                disabled={deleteMutation.isPending}
              >
                {deleteMutation.isPending ? 'Deleting...' : 'Delete Project'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function getSeverityLabel(level: number): string {
  const labels: Record<number, string> = {
    1: 'Low',
    2: 'Medium',
    3: 'High',
    4: 'Critical',
    5: 'Emergency',
  }
  return labels[level] || 'Unknown'
}

function getSeverityColor(level: number): string {
  const colors: Record<number, string> = {
    1: 'bg-green-100 text-green-800',
    2: 'bg-yellow-100 text-yellow-800',
    3: 'bg-orange-100 text-orange-800',
    4: 'bg-red-100 text-red-800',
    5: 'bg-purple-100 text-purple-800',
  }
  return colors[level] || 'bg-gray-100 text-gray-800'
}

