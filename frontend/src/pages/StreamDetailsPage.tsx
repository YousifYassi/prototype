import { useState, useRef, useEffect, useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-toastify'
import { streamApi, projectApi } from '../lib/api'
import Select, { SelectOption } from '../components/Select'
import Hls from 'hls.js'
import { 
  ArrowLeft, Play, Square, Trash2, Settings, 
  Camera, Activity, AlertCircle, Save, FolderOpen 
} from 'lucide-react'

interface StreamData {
  stream_id: string
  name: string
  source_url: string
  source_type: string
  status: string
  fps: number
  created_at: string
  updated_at: string
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

export default function StreamDetailsPage() {
  const { streamId } = useParams<{ streamId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [videoError, setVideoError] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [isEditingProject, setIsEditingProject] = useState(false)
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null)
  const [isEditingSourceUrl, setIsEditingSourceUrl] = useState(false)
  const [editedSourceUrl, setEditedSourceUrl] = useState('')
  const videoRef = useRef<HTMLVideoElement>(null)
  const videoContainerRef = useRef<HTMLDivElement>(null)
  const hlsRef = useRef<Hls | null>(null)

  // Fetch stream data
  const { data: stream, isLoading, error, refetch } = useQuery<StreamData>({
    queryKey: ['stream', streamId],
    queryFn: async () => {
      try {
        const data = await streamApi.get(streamId!)
        console.log('Stream data loaded successfully:', data)
        return data
      } catch (err) {
        console.error('Failed to load stream data:', err)
        throw err
      }
    },
    enabled: !!streamId,
    // Don't auto-refetch - only refetch manually after user actions (start/stop/update)
    // The HLS video player maintains its own connection, so polling metadata is unnecessary
    refetchInterval: false,
    refetchOnWindowFocus: false,
    retry: 1, // Only retry once on failure
  })

  // Fetch projects for reassignment
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

  // Set initial project ID and source URL when stream loads
  useEffect(() => {
    if (stream && selectedProjectId === null) {
      setSelectedProjectId(stream.project?.id || null)
    }
    if (stream && !editedSourceUrl) {
      setEditedSourceUrl(stream.source_url)
    }
  }, [stream, selectedProjectId, editedSourceUrl])

  // HLS video player setup
  useEffect(() => {
    if (!videoRef.current || !streamId || stream?.status !== 'active') {
      // Cleanup HLS if stream is not active
      if (hlsRef.current) {
        hlsRef.current.destroy()
        hlsRef.current = null
      }
      return
    }

    const token = localStorage.getItem('access_token')
    const hlsUrl = `http://localhost:8000/streams/${streamId}/hls/stream.m3u8?token=${token}`

    console.log('Setting up HLS player for:', hlsUrl)

    // Check if HLS is supported
    if (Hls.isSupported()) {
      const hls = new Hls({
        debug: false,
        enableWorker: true,
        lowLatencyMode: true,
        backBufferLength: 90,
        maxBufferLength: 30,
        maxMaxBufferLength: 60,
        maxBufferSize: 60 * 1000 * 1000,
        maxBufferHole: 0.5,
        highBufferWatchdogPeriod: 2,
        nudgeMaxRetry: 10,
        manifestLoadingTimeOut: 10000,
        manifestLoadingMaxRetry: 10,
        manifestLoadingRetryDelay: 1000,
        levelLoadingTimeOut: 10000,
        levelLoadingMaxRetry: 4,
        fragLoadingTimeOut: 20000,
        fragLoadingMaxRetry: 6,
        xhrSetup: function(xhr: XMLHttpRequest) {
          // Add authorization header to all HLS requests
          xhr.withCredentials = true
          xhr.setRequestHeader('Authorization', `Bearer ${token}`)
        },
      })

      hls.loadSource(hlsUrl)
      hls.attachMedia(videoRef.current)

      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        console.log('HLS manifest parsed, starting playback')
        videoRef.current?.play().catch(err => {
          console.error('Autoplay failed:', err)
          // Autoplay might be blocked by browser, user needs to click
        })
        setVideoError(false)
      })

      hls.on(Hls.Events.ERROR, (_event, data) => {
        console.error('HLS error:', data)
        
        if (data.fatal) {
          switch (data.type) {
            case Hls.ErrorTypes.NETWORK_ERROR:
              console.error('Fatal network error, trying to recover...')
              hls.startLoad()
              break
            case Hls.ErrorTypes.MEDIA_ERROR:
              console.error('Fatal media error, trying to recover...')
              hls.recoverMediaError()
              break
            default:
              console.error('Fatal error, cannot recover')
              setVideoError(true)
              toast.error('Video streaming error. Try restarting the stream.')
              hls.destroy()
              break
          }
        }
      })

      hlsRef.current = hls

      return () => {
        if (hlsRef.current) {
          hlsRef.current.destroy()
          hlsRef.current = null
        }
      }
    } else if (videoRef.current.canPlayType('application/vnd.apple.mpegurl')) {
      // Native HLS support (Safari)
      console.log('Using native HLS support')
      videoRef.current.src = hlsUrl
      videoRef.current.addEventListener('loadedmetadata', () => {
        videoRef.current?.play().catch(err => {
          console.error('Autoplay failed:', err)
        })
      })
      setVideoError(false)
    } else {
      console.error('HLS not supported in this browser')
      toast.error('HLS video streaming is not supported in your browser')
      setVideoError(true)
    }
  }, [streamId, stream?.status])

  // Start stream mutation
  const startMutation = useMutation({
    mutationFn: () => streamApi.start(streamId!),
    onSuccess: () => {
      toast.success('Stream started successfully')
      refetch()
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to start stream')
    },
  })

  // Stop stream mutation
  const stopMutation = useMutation({
    mutationFn: () => streamApi.stop(streamId!),
    onSuccess: () => {
      toast.success('Stream stopped')
      refetch()
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to stop stream')
    },
  })

  // Update stream mutation
  const updateMutation = useMutation({
    mutationFn: (data: { name?: string; project_id?: number; source_url?: string }) =>
      streamApi.update(streamId!, data),
    onSuccess: () => {
      toast.success('Stream updated successfully')
      setIsEditingProject(false)
      setIsEditingSourceUrl(false)
      queryClient.invalidateQueries({ queryKey: ['stream', streamId] })
      queryClient.invalidateQueries({ queryKey: ['streams'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update stream')
    },
  })

  // Delete stream mutation
  const deleteMutation = useMutation({
    mutationFn: () => streamApi.delete(streamId!),
    onSuccess: () => {
      toast.success('Stream deleted successfully')
      navigate('/streams')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete stream')
    },
  })

  const handleStart = () => {
    setVideoError(false)
    startMutation.mutate()
  }

  const handleStop = () => {
    stopMutation.mutate()
  }

  const handleDelete = () => {
    if (confirm('Are you sure you want to delete this stream? This action cannot be undone.')) {
      deleteMutation.mutate()
    }
  }

  const handleSaveProject = () => {
    if (selectedProjectId === null) {
      toast.error('Please select a project')
      return
    }
    
    updateMutation.mutate({ project_id: selectedProjectId })
  }

  const handleSaveSourceUrl = () => {
    if (!editedSourceUrl || editedSourceUrl.trim() === '') {
      toast.error('Source URL cannot be empty')
      return
    }
    
    if (stream?.status === 'active') {
      toast.error('Stream must be stopped before changing source URL')
      return
    }
    
    updateMutation.mutate({ source_url: editedSourceUrl.trim() })
  }

  const handleRetry = () => {
    setVideoError(false)
    // HLS will automatically retry when stream status becomes active
    refetch()
  }

  const handleOpenInVLC = () => {
    if (!stream) return
    
    // Create a temporary link to download a .strm file (stream file)
    // VLC can open this to play the stream
    const streamUrl = stream.source_url
    const blob = new Blob([streamUrl], { type: 'application/x-mpegurl' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${stream.name}.strm`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
    toast.info('Stream file downloaded. Open with VLC for full quality playback.')
  }

  const toggleFullscreen = () => {
    const container = videoContainerRef.current
    if (!container) return

    if (!isFullscreen) {
      if (container.requestFullscreen) {
        container.requestFullscreen()
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen()
      }
    }
    setIsFullscreen(!isFullscreen)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading stream...</p>
        </div>
      </div>
    )
  }

  if (error || !stream) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800 font-semibold mb-2">Error loading stream</p>
        {error && (
          <div className="mt-2 p-2 bg-white rounded border border-red-300">
            <p className="text-sm text-gray-700 font-mono">
              {(error as any)?.response?.data?.detail || (error as any)?.message || 'Unknown error'}
            </p>
          </div>
        )}
        <button
          onClick={() => refetch()}
          className="mt-3 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
        >
          Retry
        </button>
      </div>
    )
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <button
          onClick={() => navigate('/streams')}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Streams
        </button>
        
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{stream.name}</h1>
            <div className="flex items-center space-x-4 mt-2 text-sm text-gray-600">
              <span className="flex items-center">
                <Camera className="h-4 w-4 mr-1" />
                {getSourceTypeLabel(stream.source_type)}
              </span>
              <span>•</span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadge(stream.status)}`}>
                {stream.status}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Video Player */}
      <div className="card">
        <div
          ref={videoContainerRef}
          className="relative bg-gray-900 aspect-video cursor-pointer rounded-lg overflow-hidden"
          onClick={toggleFullscreen}
        >
          {stream.status === 'active' && !videoError ? (
            <video
              ref={videoRef}
              className="w-full h-full object-contain"
              controls
              autoPlay
              muted
              playsInline
              onError={() => {
                console.error('Video playback error')
                setVideoError(true)
              }}
            />
          ) : (
            <div className="absolute inset-0 flex items-center justify-center text-gray-400">
              {stream.status === 'error' ? (
                <div className="text-center">
                  <AlertCircle className="w-12 h-12 mx-auto mb-2" />
                  <p>Stream Error</p>
                  {stream.error_message && (
                    <p className="text-sm mt-2 max-w-md px-4">{stream.error_message}</p>
                  )}
                </div>
              ) : videoError ? (
                <div className="text-center">
                  <AlertCircle className="w-12 h-12 mx-auto mb-2" />
                  <p className="mb-3">Failed to connect to video stream</p>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleRetry()
                    }}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                  >
                    Retry Connection
                  </button>
                </div>
              ) : stream.status === 'inactive' || stream.status === 'stopped' ? (
                <div className="text-center">
                  <Camera className="w-12 h-12 mx-auto mb-2" />
                  <p>Stream not running</p>
                  <p className="text-sm mt-2">Click Start to begin streaming</p>
                </div>
              ) : (
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-2"></div>
                  <p>Loading stream...</p>
                </div>
              )}
            </div>
          )}

          {/* Detection Overlay */}
          {stream.current_result && stream.current_result.is_unsafe && (
            <div className="absolute top-4 left-4 bg-red-600 text-white px-3 py-1 rounded-lg font-semibold animate-pulse z-10">
              ⚠️ UNSAFE ACTION DETECTED
            </div>
          )}

          {/* Live Indicator */}
          {stream.status === 'active' && (
            <div className="absolute bottom-4 right-4 bg-black bg-opacity-75 text-white px-3 py-2 rounded-lg text-xs flex items-center space-x-2">
              <Activity className="h-3 w-3 animate-pulse" />
              <span>LIVE</span>
            </div>
          )}
        </div>

        {/* Current Detection */}
        {stream.current_result && (
          <div className="mt-4 p-3 bg-gray-50 rounded-lg">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-gray-700">
                Current Detection:
              </span>
              <span
                className={`text-sm font-semibold ${
                  stream.current_result.is_unsafe
                    ? 'text-red-600'
                    : 'text-green-600'
                }`}
              >
                {stream.current_result.action}
              </span>
            </div>
            <div className="mt-1">
              <div className="text-xs text-gray-600">
                Confidence: {(stream.current_result.confidence * 100).toFixed(1)}%
              </div>
              <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1">
                <div
                  className={`h-1.5 rounded-full ${
                    stream.current_result.is_unsafe ? 'bg-red-600' : 'bg-green-600'
                  }`}
                  style={{ width: `${stream.current_result.confidence * 100}%` }}
                ></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Control Panel */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Stream Controls</h3>
        
        {/* Dual Connection Warning for RTSP */}
        {stream.source_type === 'rtsp' && (
          <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
            <p className="text-sm text-amber-800">
              <strong>📡 Dual Connection Notice:</strong> This system uses two connections to your camera:
              <br />
              • AI Detection (OpenCV) for analyzing safety violations
              <br />
              • Browser Streaming (FFmpeg) for live video preview
              <br />
              <br />
              If you encounter connection errors, consider:
              <br />
              • Using a substream URL (e.g., /stream2 instead of /stream1)
              <br />
              • Rebooting your camera to free up connections
              <br />
              • Using "Open in VLC" for full quality playback without browser streaming
            </p>
          </div>
        )}
        
        <div className="flex flex-wrap gap-3">
          {(stream.status === 'inactive' || stream.status === 'stopped' || stream.status === 'error') && (
            <button
              onClick={handleStart}
              disabled={startMutation.isPending}
              className="btn-primary flex items-center disabled:opacity-50"
            >
              <Play className="h-4 w-4 mr-2" />
              {startMutation.isPending ? 'Starting...' : 'Start Stream'}
            </button>
          )}
          
          {stream.status === 'active' && (
            <>
              <button
                onClick={handleStop}
                disabled={stopMutation.isPending}
                className="bg-yellow-600 text-white px-4 py-2 rounded-lg hover:bg-yellow-700 transition-colors flex items-center disabled:opacity-50"
              >
                <Square className="h-4 w-4 mr-2" />
                {stopMutation.isPending ? 'Stopping...' : 'Stop Stream'}
              </button>
              
              <button
                onClick={handleOpenInVLC}
                className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors flex items-center"
                title="Download stream file to open in VLC for full quality"
              >
                <Camera className="h-4 w-4 mr-2" />
                Open in VLC
              </button>
            </>
          )}
          
          <button
            onClick={handleDelete}
            disabled={deleteMutation.isPending}
            className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors flex items-center disabled:opacity-50"
          >
            <Trash2 className="h-4 w-4 mr-2" />
            {deleteMutation.isPending ? 'Deleting...' : 'Delete Stream'}
          </button>
        </div>
        
        {stream.status === 'active' && (
          <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-800">
              💡 <strong>Tip:</strong> The browser shows a preview (~5 FPS). 
              Click "Open in VLC" to view the stream at full quality in VLC Media Player.
            </p>
          </div>
        )}
        
        {stream.error_message && stream.error_message.includes('connection limit') && (
          <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-800">
              ⚠️ <strong>Camera Connection Limit:</strong> Your camera may have reached its maximum connection limit. 
              Both AI detection and browser viewing connect to the camera simultaneously. 
              Try using a substream URL (e.g., /stream2 instead of /stream1) or reboot your camera.
            </p>
          </div>
        )}
      </div>

      {/* Project Assignment */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Project Assignment</h3>
          {!isEditingProject && (
            <button
              onClick={() => setIsEditingProject(true)}
              className="btn-secondary flex items-center"
            >
              <Settings className="h-4 w-4 mr-2" />
              Change Project
            </button>
          )}
        </div>
        
        {!isEditingProject ? (
          <div>
            {stream.project ? (
              <div className="flex items-start space-x-3 p-4 bg-gray-50 rounded-lg">
                <FolderOpen className="h-5 w-5 text-blue-600 mt-0.5" />
                <div>
                  <p className="font-medium text-gray-900">{stream.project.name}</p>
                  <p className="text-sm text-gray-600">
                    {stream.project.jurisdiction.name} - {stream.project.industry.name}
                  </p>
                </div>
              </div>
            ) : (
              <p className="text-gray-600">No project assigned</p>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            <Select
              value={selectedProjectId || ''}
              onChange={(value) => setSelectedProjectId(value ? Number(value) : null)}
              options={projectOptions}
              placeholder="Select a project"
            />
            <div className="flex gap-2">
              <button
                onClick={handleSaveProject}
                disabled={updateMutation.isPending}
                className="btn-primary flex items-center disabled:opacity-50"
              >
                <Save className="h-4 w-4 mr-2" />
                {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
              </button>
              <button
                onClick={() => {
                  setIsEditingProject(false)
                  setSelectedProjectId(stream.project?.id || null)
                }}
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Stream Stats */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Stream Statistics</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <Activity className="h-6 w-6 text-blue-600 mx-auto mb-2" />
            <p className="text-2xl font-bold text-gray-900">{stream.fps}</p>
            <p className="text-sm text-gray-600">FPS</p>
          </div>
          
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <Camera className="h-6 w-6 text-green-600 mx-auto mb-2" />
            <p className="text-2xl font-bold text-gray-900">
              {stream.width}x{stream.height}
            </p>
            <p className="text-sm text-gray-600">Resolution</p>
          </div>
          
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <Activity className="h-6 w-6 text-purple-600 mx-auto mb-2" />
            <p className="text-2xl font-bold text-gray-900">{stream.frame_count}</p>
            <p className="text-sm text-gray-600">Frames</p>
          </div>
          
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <AlertCircle className="h-6 w-6 text-red-600 mx-auto mb-2" />
            <p className="text-2xl font-bold text-gray-900">{stream.error_count}</p>
            <p className="text-sm text-gray-600">Errors</p>
          </div>
        </div>
        
        {stream.error_message && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">{stream.error_message}</p>
          </div>
        )}
      </div>

      {/* Stream Info */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Stream Information</h3>
          {!isEditingSourceUrl && stream.status !== 'active' && (
            <button
              onClick={() => setIsEditingSourceUrl(true)}
              className="btn-secondary flex items-center text-sm"
            >
              <Settings className="h-4 w-4 mr-2" />
              Edit Source URL
            </button>
          )}
        </div>
        
        {isEditingSourceUrl ? (
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Source URL
            </label>
            <input
              type="text"
              value={editedSourceUrl}
              onChange={(e) => setEditedSourceUrl(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
              placeholder="rtsp://username:password@192.168.1.100:554/stream1"
            />
            <div className="mt-2 flex gap-2">
              <button
                onClick={handleSaveSourceUrl}
                disabled={updateMutation.isPending}
                className="btn-primary flex items-center disabled:opacity-50 text-sm"
              >
                <Save className="h-4 w-4 mr-2" />
                {updateMutation.isPending ? 'Saving...' : 'Save URL'}
              </button>
              <button
                onClick={() => {
                  setIsEditingSourceUrl(false)
                  setEditedSourceUrl(stream.source_url)
                }}
                className="btn-secondary text-sm"
              >
                Cancel
              </button>
            </div>
            <p className="mt-2 text-xs text-gray-600">
              ⚠️ Stream must be stopped to change the source URL
            </p>
          </div>
        ) : null}
        
        <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {!isEditingSourceUrl && (
            <div>
              <dt className="text-sm font-medium text-gray-600">Source URL</dt>
              <dd className="mt-1 text-sm text-gray-900 font-mono break-all">
                {stream.source_url}
              </dd>
            </div>
          )}
          
          <div>
            <dt className="text-sm font-medium text-gray-600">Source Type</dt>
            <dd className="mt-1 text-sm text-gray-900">
              {getSourceTypeLabel(stream.source_type)}
            </dd>
          </div>
          
          <div>
            <dt className="text-sm font-medium text-gray-600">Created</dt>
            <dd className="mt-1 text-sm text-gray-900">
              {new Date(stream.created_at).toLocaleString()}
            </dd>
          </div>
          
          <div>
            <dt className="text-sm font-medium text-gray-600">Last Updated</dt>
            <dd className="mt-1 text-sm text-gray-900">
              {new Date(stream.updated_at).toLocaleString()}
            </dd>
          </div>
        </dl>
      </div>
    </div>
  )
}

