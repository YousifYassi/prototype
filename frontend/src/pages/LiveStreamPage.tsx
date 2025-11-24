import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { toast } from 'react-toastify'
import { streamApi, projectApi } from '../lib/api'
import Select, { SelectOption } from '../components/Select'
import { 
  Plus, Camera, Video, AlertCircle, Play, 
  Activity, FolderOpen, MapPin
} from 'lucide-react'

interface Stream {
  stream_id: string
  name: string
  status: string
  source_type: string
  fps: number
  width: number
  height: number
  frame_count: number
  error_count: number
  last_frame_time: string | null
  last_detection_time: string | null
  current_result: {
    action: string
    confidence: number
    alert: boolean
    is_unsafe: boolean
  } | null
  error_message: string | null
  project: {
    id: number
    name: string
    jurisdiction: {
      id: number
      name: string
      code: string
    }
    industry: {
      id: number
      name: string
      code: string
    }
  } | null
}

interface StreamFormData {
  name: string
  source_url: string
  source_type: 'rtsp' | 'rtmp' | 'http' | 'webcam'
  project_id: number | null
  fps: number
}

export default function LiveStreamPage() {
  const navigate = useNavigate()
  const [showAddForm, setShowAddForm] = useState(false)
  const [showCameraGuide, setShowCameraGuide] = useState(false)
  const [formData, setFormData] = useState<StreamFormData>({
    name: '',
    source_url: '',
    source_type: 'rtsp',
    project_id: null,
    fps: 30,
  })
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Fetch streams
  const { data: streamsData, isLoading, error, refetch } = useQuery({
    queryKey: ['streams'],
    queryFn: streamApi.list,
    refetchInterval: 15000, // Refresh every 15 seconds
    refetchOnWindowFocus: false, // Don't refetch when window regains focus
  })

  // Fetch projects
  const { data: projectsData } = useQuery({
    queryKey: ['projects'],
    queryFn: projectApi.list,
  })

  const projectOptions: SelectOption[] = useMemo(() => 
    projectsData?.projects.map((project: any) => ({
      value: project.id,
      label: project.name,
      description: `${project.jurisdiction.name} - ${project.industry.name}`
    })) || [],
    [projectsData]
  )

  const sourceTypeOptions: SelectOption[] = [
    { value: 'rtsp', label: 'RTSP Camera', description: 'IP cameras with RTSP protocol' },
    { value: 'rtmp', label: 'RTMP Stream', description: 'Real-Time Messaging Protocol' },
    { value: 'http', label: 'HTTP Stream', description: 'HTTP/MJPEG stream' },
    { value: 'webcam', label: 'Webcam', description: 'Local USB webcam' },
  ]

  const handleAddStream = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.project_id) {
      toast.error('Please select a project')
      return
    }

    setIsSubmitting(true)

    try {
      await streamApi.create({
        name: formData.name,
        source_url: formData.source_url,
        source_type: formData.source_type,
        project_id: formData.project_id,
        fps: formData.fps,
      })
      
      toast.success('Stream created successfully! Click on it to start streaming.')
      setShowAddForm(false)
      setFormData({
        name: '',
        source_url: '',
        source_type: 'rtsp',
        project_id: null,
        fps: 30,
      })
      refetch()
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to create stream')
    } finally {
      setIsSubmitting(false)
    }
  }

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      active: 'bg-green-100 text-green-800',
      inactive: 'bg-gray-100 text-gray-800',
      stopped: 'bg-yellow-100 text-yellow-800',
      error: 'bg-red-100 text-red-800',
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const getSourceTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      rtsp: 'RTSP Camera',
      rtmp: 'RTMP Stream',
      http: 'HTTP Stream',
      webcam: 'Webcam',
    }
    return labels[type] || type
  }

  const getSourceTypeIcon = (type: string) => {
    switch (type) {
      case 'rtsp':
      case 'rtmp':
      case 'http':
        return <Camera className="h-5 w-5" />
      case 'webcam':
        return <Video className="h-5 w-5" />
      default:
        return <Camera className="h-5 w-5" />
    }
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">Error loading streams. Please try again.</p>
      </div>
    )
  }

  const streams = streamsData?.streams || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Live Video Streams</h1>
          <p className="text-gray-600 mt-1">
            Create and manage live camera feeds with real-time safety detection
          </p>
        </div>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center"
        >
          <Plus className="h-5 w-5 mr-2" />
          {showAddForm ? 'Cancel' : 'Add Stream'}
        </button>
      </div>

      {/* Add Stream Form */}
      {showAddForm && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Add New Stream</h2>
          <form onSubmit={handleAddStream} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Stream Name
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="input"
                placeholder="e.g., Warehouse Camera 1"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Source Type
              </label>
              <Select
                value={formData.source_type}
                onChange={(value) => setFormData({ ...formData, source_type: value as StreamFormData['source_type'] })}
                options={sourceTypeOptions}
                placeholder="Select source type"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Source URL
              </label>
              <input
                type="text"
                value={formData.source_url}
                onChange={(e) =>
                  setFormData({ ...formData, source_url: e.target.value })
                }
                className="input"
                placeholder={
                  formData.source_type === 'webcam'
                    ? '0 (for default webcam)'
                    : formData.source_type === 'rtsp'
                    ? 'rtsp://username:password@192.168.1.100:554/stream'
                    : 'Stream URL'
                }
                required
              />
              <p className="text-xs text-gray-500 mt-1">
                {formData.source_type === 'webcam'
                  ? 'Enter camera index (usually 0 for default webcam)'
                  : formData.source_type === 'rtsp'
                  ? 'Format: rtsp://[username:password@]ip:port/path'
                  : 'Enter the full stream URL'}
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Project *
              </label>
              <Select
                value={formData.project_id || ''}
                onChange={(value) => setFormData({ ...formData, project_id: value ? Number(value) : null })}
                options={projectOptions}
                placeholder="Select a project"
              />
              <p className="text-xs text-gray-500 mt-1">
                Streams must be associated with a project for jurisdiction-specific monitoring
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                FPS (Frames Per Second)
              </label>
              <input
                type="number"
                value={formData.fps}
                onChange={(e) =>
                  setFormData({ ...formData, fps: parseInt(e.target.value) })
                }
                className="input"
                min="1"
                max="60"
                required
              />
            </div>

            <div className="flex gap-2">
              <button
                type="submit"
                disabled={isSubmitting}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {isSubmitting ? 'Creating...' : 'Create Stream'}
              </button>
              <button
                type="button"
                onClick={() => setShowAddForm(false)}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Camera Setup Guide */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-semibold text-blue-900 mb-2">
          📹 Camera Setup Guide
        </h3>
        <p className="text-sm text-blue-800 mb-2">
          Need help choosing a camera? We recommend:
        </p>
        <ul className="text-sm text-blue-800 space-y-1 ml-4">
          <li>• <strong>Budget:</strong> Wyze Cam v3 or Reolink E1 Pro</li>
          <li>• <strong>Professional:</strong> Hikvision DS-2CD2XXX or Axis M-Series</li>
          <li>• <strong>Industrial:</strong> Dahua IPC-HFW or Bosch FLEXIDOME</li>
        </ul>
        <button
          onClick={() => setShowCameraGuide(true)}
          className="text-sm text-blue-600 hover:text-blue-700 font-medium mt-2 inline-block underline"
        >
          View detailed camera recommendations →
        </button>
      </div>

      {/* Camera Guide Modal - Keeping existing modal code */}
      {showCameraGuide && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            <div className="flex justify-between items-center p-6 border-b border-gray-200">
              <h2 className="text-2xl font-bold text-gray-900">
                📹 Camera Setup Guide
              </h2>
              <button
                onClick={() => setShowCameraGuide(false)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="overflow-y-auto p-6">
              <p className="text-gray-600 mb-4">
                For detailed camera setup instructions, please refer to the CAMERA_SETUP_GUIDE.md file in the project documentation.
              </p>
            </div>
            <div className="border-t border-gray-200 p-4 bg-gray-50">
              <button
                onClick={() => setShowCameraGuide(false)}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Streams List */}
      {streams.length === 0 ? (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <Camera className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            No streams configured
          </h3>
          <p className="text-gray-600 mb-4">
            Add a camera or video stream to start monitoring
          </p>
          <button
            onClick={() => setShowAddForm(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Add Your First Stream
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {streams.map((stream: Stream) => (
            <div
              key={stream.stream_id}
              onClick={() => navigate(`/streams/${stream.stream_id}`)}
              className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer overflow-hidden"
            >
              {/* Stream Preview Area */}
              <div className="relative bg-gray-900 aspect-video flex items-center justify-center">
                <div className="text-gray-400 text-center">
                  {getSourceTypeIcon(stream.source_type)}
                  <p className="text-sm mt-2">
                    {stream.status === 'active' ? 'Streaming' : 'Not Active'}
                  </p>
                </div>
                
                {/* Status Badge on Preview */}
                <div className={`absolute top-2 right-2 px-2 py-1 rounded text-xs font-medium ${getStatusBadge(stream.status)}`}>
                  {stream.status}
                </div>

                {/* Live indicator for active streams */}
                {stream.status === 'active' && (
                  <div className="absolute top-2 left-2 flex items-center space-x-1 bg-red-600 text-white px-2 py-1 rounded text-xs font-medium">
                    <Activity className="h-3 w-3 animate-pulse" />
                    <span>LIVE</span>
                  </div>
                )}
              </div>

              {/* Stream Info */}
              <div className="p-4">
                <div className="flex justify-between items-start mb-3">
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-lg text-gray-900 truncate">
                      {stream.name}
                    </h3>
                    <p className="text-sm text-gray-500">
                      {getSourceTypeLabel(stream.source_type)}
                    </p>
                  </div>
                </div>

                {/* Project Info */}
                {stream.project && (
                  <div className="mb-3 p-2 bg-gray-50 rounded text-xs">
                    <div className="flex items-center text-gray-600 mb-1">
                      <FolderOpen className="h-3 w-3 mr-1" />
                      <span className="font-medium truncate">{stream.project.name}</span>
                    </div>
                    <div className="flex items-center text-gray-500">
                      <MapPin className="h-3 w-3 mr-1" />
                      <span className="truncate">{stream.project.jurisdiction.name}</span>
                    </div>
                  </div>
                )}

                {/* Stream Stats */}
                <div className="flex items-center justify-between text-xs text-gray-600 pt-3 border-t border-gray-200">
                  <span>{stream.fps} FPS</span>
                  <span>•</span>
                  <span>{stream.frame_count} frames</span>
                  {stream.error_count > 0 && (
                    <>
                      <span>•</span>
                      <span className="text-red-600 flex items-center">
                        <AlertCircle className="h-3 w-3 mr-1" />
                        {stream.error_count}
                      </span>
                    </>
                  )}
                </div>

                {/* Click to view indicator */}
                <div className="mt-3 flex items-center justify-center text-sm text-blue-600">
                  <Play className="h-4 w-4 mr-1" />
                  Click to view & control
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
