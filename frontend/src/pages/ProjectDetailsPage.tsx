import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, useNavigate } from 'react-router-dom'
import { toast } from 'react-toastify'
import { projectApi } from '../lib/api'
import { 
  ArrowLeft, Settings, FileText, Camera, FileVideo, 
  Trash2, AlertTriangle, Shield, ExternalLink, CheckCircle, Clock, Play, Save, Building2 
} from 'lucide-react'
import SeveritySelector from '../components/SeveritySelector'

export default function ProjectDetailsPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<'overview' | 'regulations' | 'settings'>('overview')
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [editFormData, setEditFormData] = useState({
    name: '',
    min_severity_alert: 1,
  })

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

  const updateMutation = useMutation({
    mutationFn: (data: { name?: string; min_severity_alert?: number }) => 
      projectApi.update(parseInt(projectId!), data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project', projectId] })
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      toast.success('Project updated successfully')
      setIsEditing(false)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update project')
    },
  })

  const handleStartEdit = () => {
    if (project) {
      setEditFormData({
        name: project.name,
        min_severity_alert: project.min_severity_alert,
      })
      setIsEditing(true)
    }
  }

  const handleSaveChanges = () => {
    if (!editFormData.name.trim()) {
      toast.error('Please enter a project name')
      return
    }

    updateMutation.mutate({
      name: editFormData.name,
      min_severity_alert: editFormData.min_severity_alert,
    })
  }

  const handleCancelEdit = () => {
    setIsEditing(false)
  }

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
                  <p className="text-2xl font-bold text-gray-900 mt-1">
                    {project.stats?.active_streams || 0}
                  </p>
                </div>
                <Camera className="h-8 w-8 text-blue-500" />
              </div>
            </div>

            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Videos Processed</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">
                    {project.stats?.total_videos || 0}
                  </p>
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

          {/* Associated Videos */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Associated Videos</h3>
              {project.videos && project.videos.length > 0 && (
                <div className="flex items-center space-x-2 text-sm">
                  {project.stats && (
                    <>
                      <span className="flex items-center text-green-600">
                        <CheckCircle className="h-4 w-4 mr-1" />
                        {project.stats.safe_videos} safe
                      </span>
                      {project.stats.unsafe_videos > 0 && (
                        <span className="flex items-center text-red-600">
                          <AlertTriangle className="h-4 w-4 mr-1" />
                          {project.stats.unsafe_videos} unsafe
                        </span>
                      )}
                      {project.stats.processing_videos > 0 && (
                        <span className="flex items-center text-blue-600">
                          <Clock className="h-4 w-4 mr-1" />
                          {project.stats.processing_videos} processing
                        </span>
                      )}
                    </>
                  )}
                </div>
              )}
            </div>
            {project.videos && project.videos.length > 0 ? (
              <div className="space-y-2">
                {project.videos.map((video: any) => (
                  <div
                    key={video.video_id}
                    className="flex items-center justify-between py-3 px-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                    onClick={() => navigate(`/video/${video.video_id}`)}
                  >
                    <div className="flex items-center space-x-3 flex-1 min-w-0">
                      <FileVideo className="h-5 w-5 text-gray-400 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-gray-900 truncate">{video.filename}</p>
                        <p className="text-sm text-gray-500">
                          Uploaded {new Date(video.uploaded_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getVideoStatusColor(video.status)}`}>
                        {video.status.replace('_', ' ')}
                      </span>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          navigate(`/video/${video.video_id}`)
                        }}
                        className="text-blue-600 hover:text-blue-700"
                      >
                        <Play className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <FileVideo className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-600 mb-4">No videos uploaded to this project yet</p>
                <button
                  onClick={() => navigate('/upload')}
                  className="btn-primary"
                >
                  Upload First Video
                </button>
              </div>
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
          <div className="flex justify-between items-center mb-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Project Settings</h3>
              <p className="text-sm text-gray-600 mt-1">
                Update project configuration and settings
              </p>
            </div>
            {!isEditing && (
              <button
                onClick={handleStartEdit}
                className="btn-primary flex items-center"
              >
                <Settings className="h-4 w-4 mr-2" />
                Edit Settings
              </button>
            )}
          </div>
          
          {!isEditing ? (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Project Name
                </label>
                <p className="text-gray-900 text-lg">{project.name}</p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Jurisdiction
                  </label>
                  <div className="flex items-center space-x-2">
                    <Shield className="h-4 w-4 text-blue-600" />
                    <p className="text-gray-900">{project.jurisdiction.name} ({project.jurisdiction.code.toUpperCase()})</p>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">Cannot be changed after creation</p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Industry
                  </label>
                  <div className="flex items-center space-x-2">
                    <Building2 className="h-4 w-4 text-green-600" />
                    <p className="text-gray-900">{project.industry.name}</p>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">Cannot be changed after creation</p>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Minimum Alert Severity
                </label>
                <div className={`inline-flex px-4 py-2 rounded-lg font-medium ${getSeverityColor(project.min_severity_alert)}`}>
                  {getSeverityLabel(project.min_severity_alert)}
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Only violations at this severity level or higher will trigger alerts
                </p>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start space-x-2">
                  <AlertTriangle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div className="text-sm text-blue-800">
                    <p className="font-medium mb-1">Note About Jurisdiction & Industry</p>
                    <p>
                      Jurisdiction and industry cannot be changed after project creation as they determine
                      the applicable safety regulations and severity mappings. If you need different
                      regulations, please create a new project.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <form onSubmit={(e) => { e.preventDefault(); handleSaveChanges(); }} className="space-y-6">
              <div>
                <label htmlFor="edit-name" className="block text-sm font-medium text-gray-700 mb-2">
                  Project Name *
                </label>
                <input
                  type="text"
                  id="edit-name"
                  value={editFormData.name}
                  onChange={(e) => setEditFormData({ ...editFormData, name: e.target.value })}
                  placeholder="e.g., Main Restaurant Kitchen"
                  className="input"
                  required
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Jurisdiction
                  </label>
                  <div className="input bg-gray-50 cursor-not-allowed flex items-center space-x-2">
                    <Shield className="h-4 w-4 text-blue-600" />
                    <span className="text-gray-600">{project.jurisdiction.name}</span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">Cannot be changed</p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Industry
                  </label>
                  <div className="input bg-gray-50 cursor-not-allowed flex items-center space-x-2">
                    <Building2 className="h-4 w-4 text-green-600" />
                    <span className="text-gray-600">{project.industry.name}</span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">Cannot be changed</p>
                </div>
              </div>

              <div>
                <label htmlFor="edit-severity" className="block text-sm font-medium text-gray-700 mb-2">
                  Minimum Alert Severity *
                </label>
                <SeveritySelector
                  value={editFormData.min_severity_alert}
                  onChange={(value) => setEditFormData({ ...editFormData, min_severity_alert: value })}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Set the minimum severity level to trigger alerts and notifications
                </p>
              </div>

              <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
                <button
                  type="button"
                  onClick={handleCancelEdit}
                  className="btn-secondary"
                  disabled={updateMutation.isPending}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={updateMutation.isPending}
                  className="btn-primary flex items-center disabled:opacity-50"
                >
                  <Save className="h-4 w-4 mr-2" />
                  {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          )}
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

function getVideoStatusColor(status: string): string {
  const colors: Record<string, string> = {
    'safe': 'bg-green-100 text-green-800',
    'unsafe_detected': 'bg-red-100 text-red-800',
    'processing': 'bg-blue-100 text-blue-800',
    'uploaded': 'bg-gray-100 text-gray-800',
    'error': 'bg-orange-100 text-orange-800',
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

