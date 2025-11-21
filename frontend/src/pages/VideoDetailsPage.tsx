import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, useNavigate } from 'react-router-dom'
import { videoApi, projectApi } from '../lib/api'
import { 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  FileVideo, 
  ArrowLeft,
  Download,
  Calendar,
  Activity,
  Play,
  FolderOpen,
  Building2,
  Shield
} from 'lucide-react'
import { useState, useMemo } from 'react'
import { toast } from 'react-toastify'
import Select, { SelectOption } from '../components/Select'

export default function VideoDetailsPage() {
  const { videoId } = useParams<{ videoId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [showVideo, setShowVideo] = useState(false)

  const { data: video, isLoading, error } = useQuery({
    queryKey: ['video', videoId],
    queryFn: () => videoApi.getStatus(videoId!),
    enabled: !!videoId,
    refetchInterval: (query) => {
      // Auto-refresh if still processing
      const data = query.state.data as any
      if (data?.status === 'processing' || data?.status === 'uploaded') {
        return 3000 // Refresh every 3 seconds
      }
      return false
    }
  })

  // Fetch projects for project selector
  const { data: projectsData } = useQuery({
    queryKey: ['projects'],
    queryFn: projectApi.list,
  })

  const projectOptions: SelectOption[] = useMemo(() => {
    const options: SelectOption[] = [
      { value: '', label: 'No project', description: 'Use default settings' }
    ];
    if (projectsData?.projects) {
      const projectOpts = projectsData.projects.map((project: any) => ({
        value: project.id,
        label: project.name,
        description: `${project.jurisdiction.name} - ${project.industry.name}`
      }));
      options.push(...projectOpts);
    }
    return options;
  }, [projectsData]);

  // Mutation for updating project assignment
  const updateProjectMutation = useMutation({
    mutationFn: ({ videoId, projectId }: { videoId: string; projectId: number | null }) =>
      videoApi.updateProject(videoId, projectId),
    onSuccess: () => {
      toast.success('Project assignment updated successfully!')
      queryClient.invalidateQueries({ queryKey: ['video', videoId] })
      queryClient.invalidateQueries({ queryKey: ['videos'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update project assignment')
    },
  })

  const handleProjectChange = (newProjectId: string | number) => {
    const projectId = newProjectId ? Number(newProjectId) : null
    updateProjectMutation.mutate({ videoId: videoId!, projectId })
  }

  const handleDownload = () => {
    if (!videoId) return
    const downloadUrl = videoApi.getDownloadUrl(videoId)
    window.open(downloadUrl, '_blank')
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'safe':
        return 'text-green-600 bg-green-100 border-green-200'
      case 'unsafe_detected':
        return 'text-red-600 bg-red-100 border-red-200'
      case 'processing':
        return 'text-blue-600 bg-blue-100 border-blue-200'
      case 'uploaded':
        return 'text-gray-600 bg-gray-100 border-gray-200'
      case 'error':
        return 'text-orange-600 bg-orange-100 border-orange-200'
      default:
        return 'text-gray-600 bg-gray-100 border-gray-200'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'safe':
        return <CheckCircle className="h-6 w-6" />
      case 'unsafe_detected':
        return <AlertTriangle className="h-6 w-6" />
      case 'processing':
      case 'uploaded':
        return <Clock className="h-6 w-6" />
      default:
        return <FileVideo className="h-6 w-6" />
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading video details...</p>
        </div>
      </div>
    )
  }

  if (error || !video) {
    return (
      <div className="space-y-6">
        <button
          onClick={() => navigate('/')}
          className="flex items-center text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="h-5 w-5 mr-2" />
          Back to Dashboard
        </button>
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center">
            <AlertTriangle className="h-6 w-6 text-red-600 mr-3" />
            <div>
              <h3 className="text-lg font-semibold text-red-900">Error Loading Video</h3>
              <p className="text-red-700 mt-1">
                {error?.message || 'Video not found or you do not have permission to view it.'}
              </p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const result = video.result || {}
  const unsafeActions = result.unsafe_actions || []

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <button
        onClick={() => navigate('/')}
        className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
      >
        <ArrowLeft className="h-5 w-5 mr-2" />
        Back to Dashboard
      </button>

      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-4">
            <div className="flex-shrink-0">
              <FileVideo className="h-12 w-12 text-blue-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{video.filename}</h1>
              <p className="text-gray-600 mt-1">Video ID: {video.video_id}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={handleDownload}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Download className="h-4 w-4" />
              Download
            </button>
            <div className={`flex items-center space-x-2 px-4 py-2 rounded-lg border ${getStatusColor(video.status)}`}>
              {getStatusIcon(video.status)}
              <span className="font-semibold capitalize">
                {video.status.replace('_', ' ')}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Video Player */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Play className="h-5 w-5 mr-2 text-gray-600" />
          Video Preview
        </h2>
        {!showVideo ? (
          <div 
            className="relative bg-gray-900 rounded-lg overflow-hidden cursor-pointer group aspect-video"
            onClick={() => setShowVideo(true)}
          >
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <div className="bg-white/90 group-hover:bg-white rounded-full p-6 mb-3 inline-block transition-colors">
                  <Play className="h-12 w-12 text-blue-600" />
                </div>
                <p className="text-white text-lg font-medium">Click to load video</p>
                <p className="text-gray-300 text-sm mt-1">Original uploaded video</p>
              </div>
            </div>
            <div className="absolute inset-0 bg-gradient-to-b from-transparent to-black/50"></div>
          </div>
        ) : (
          <div className="relative bg-gray-900 rounded-lg overflow-hidden">
            <video 
              controls 
              autoPlay
              className="w-full aspect-video"
              src={videoApi.getStreamUrl(videoId!)}
            >
              Your browser does not support the video tag.
            </video>
          </div>
        )}
        <p className="text-sm text-gray-500 mt-3">
          This is the original video file you uploaded. Detection results are shown below.
        </p>
      </div>

      {/* Project Assignment */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <FolderOpen className="h-5 w-5 mr-2 text-gray-600" />
          Project Assignment
        </h2>
        <div className="space-y-3">
          <div>
            <label htmlFor="video-project" className="block text-sm font-medium text-gray-700 mb-2">
              Assign to Project
            </label>
            <Select
              value={video?.project?.id || ''}
              onChange={handleProjectChange}
              options={projectOptions}
              placeholder="Select a project"
              disabled={updateProjectMutation.isPending}
            />
            <p className="mt-2 text-xs text-gray-500">
              Change the project assignment to apply different jurisdiction and industry-specific safety rules
            </p>
          </div>
          {video?.project && (
            <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2 text-sm">
                  <Shield className="h-4 w-4 text-blue-600" />
                  <span className="font-medium text-blue-900">{video.project.jurisdiction?.name}</span>
                  {video.project.industry && (
                    <>
                      <span className="text-blue-400">•</span>
                      <Building2 className="h-4 w-4 text-blue-600" />
                      <span className="font-medium text-blue-900">{video.project.industry.name}</span>
                    </>
                  )}
                </div>
                <button
                  onClick={() => navigate(`/projects/${video.project.id}`)}
                  className="px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-xs flex items-center"
                >
                  View Project
                  <ArrowLeft className="h-3 w-3 ml-1 rotate-180" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Processing Status */}
      {(video.status === 'processing' || video.status === 'uploaded') && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-center">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mr-3"></div>
            <div>
              <h3 className="font-semibold text-blue-900">Processing Video</h3>
              <p className="text-blue-700 text-sm mt-1">
                Your video is being analyzed. This page will update automatically when complete.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Video Info Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Upload Information */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Calendar className="h-5 w-5 mr-2 text-gray-600" />
            Upload Information
          </h2>
          <div className="space-y-3">
            <div>
              <p className="text-sm text-gray-600">Uploaded At</p>
              <p className="font-medium text-gray-900">
                {new Date(video.uploaded_at).toLocaleString()}
              </p>
            </div>
            {video.processed_at && (
              <div>
                <p className="text-sm text-gray-600">Processed At</p>
                <p className="font-medium text-gray-900">
                  {new Date(video.processed_at).toLocaleString()}
                </p>
              </div>
            )}
            <div>
              <p className="text-sm text-gray-600">Filename</p>
              <p className="font-medium text-gray-900 break-all">{video.filename}</p>
            </div>
          </div>
        </div>

        {/* Detection Summary */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Activity className="h-5 w-5 mr-2 text-gray-600" />
            Detection Summary
          </h2>
          <div className="space-y-3">
            <div>
              <p className="text-sm text-gray-600">Status</p>
              <p className={`font-semibold text-lg capitalize ${
                video.status === 'safe' ? 'text-green-600' : 
                video.status === 'unsafe_detected' ? 'text-red-600' : 
                'text-gray-600'
              }`}>
                {video.status.replace('_', ' ')}
              </p>
            </div>
            {result.total_detections !== undefined && (
              <div>
                <p className="text-sm text-gray-600">Total Detections</p>
                <p className="font-medium text-gray-900 text-lg">
                  {result.total_detections}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>


      {/* Unsafe Actions Detected */}
      {video.status === 'unsafe_detected' && unsafeActions.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <AlertTriangle className="h-5 w-5 mr-2 text-red-600" />
            Unsafe Actions Detected
          </h2>
          <div className="space-y-4">
            {unsafeActions.map((detection: any, index: number) => (
              <div 
                key={index}
                className="border border-red-200 bg-red-50 rounded-lg p-4"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <AlertTriangle className="h-5 w-5 text-red-600" />
                      <h3 className="font-semibold text-red-900 capitalize">
                        {detection.action.replace('_', ' ')}
                      </h3>
                    </div>
                    <div className="mt-2 space-y-1">
                      <p className="text-sm text-red-800">
                        <span className="font-medium">Confidence:</span>{' '}
                        {(detection.confidence * 100).toFixed(1)}%
                      </p>
                      {detection.timestamp && (
                        <p className="text-sm text-red-800">
                          <span className="font-medium">Detected At:</span>{' '}
                          {new Date(detection.timestamp).toLocaleString()}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="ml-4">
                    <div className="w-20 h-20 bg-red-100 rounded-lg flex items-center justify-center">
                      <AlertTriangle className="h-10 w-10 text-red-600" />
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Safe Result */}
      {video.status === 'safe' && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <div className="flex items-center">
            <CheckCircle className="h-8 w-8 text-green-600 mr-3" />
            <div>
              <h3 className="text-lg font-semibold text-green-900">All Clear!</h3>
              <p className="text-green-700 mt-1">
                No unsafe actions were detected in this video. Great work maintaining workplace safety!
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Error Result */}
      {video.status === 'error' && result.error && (
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-6">
          <div className="flex items-start">
            <AlertTriangle className="h-6 w-6 text-orange-600 mr-3 mt-0.5" />
            <div>
              <h3 className="font-semibold text-orange-900">Processing Error</h3>
              <p className="text-orange-700 mt-1">{result.error}</p>
              <p className="text-orange-600 text-sm mt-2">
                Please try uploading the video again. If the problem persists, check that the video file is valid and not corrupted.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex space-x-3">
        <button
          onClick={() => navigate('/')}
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
        >
          Back to Dashboard
        </button>
        <button
          onClick={() => navigate('/upload')}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Upload Another Video
        </button>
      </div>
    </div>
  )
}

