import { useQuery } from '@tanstack/react-query'
import { videoApi } from '../lib/api'
import { AlertTriangle, CheckCircle, Clock, FileVideo, TrendingUp } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function Dashboard() {
  const { data: videosData, isLoading } = useQuery({
    queryKey: ['videos'],
    queryFn: () => videoApi.list(10, 0),
  })

  const videos = videosData?.videos || []
  const unsafeVideos = videos.filter((v: any) => v.status === 'unsafe_detected')
  const safeVideos = videos.filter((v: any) => v.status === 'safe')
  const processingVideos = videos.filter((v: any) => 
    v.status === 'uploaded' || v.status === 'processing'
  )

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'safe':
        return 'text-green-600 bg-green-100'
      case 'unsafe_detected':
        return 'text-red-600 bg-red-100'
      case 'processing':
        return 'text-blue-600 bg-blue-100'
      case 'uploaded':
        return 'text-gray-600 bg-gray-100'
      case 'error':
        return 'text-orange-600 bg-orange-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'safe':
        return <CheckCircle className="h-5 w-5" />
      case 'unsafe_detected':
        return <AlertTriangle className="h-5 w-5" />
      case 'processing':
      case 'uploaded':
        return <Clock className="h-5 w-5" />
      default:
        return <FileVideo className="h-5 w-5" />
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Monitor your workplace safety video analysis
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <FileVideo className="h-6 w-6 text-gray-400" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Total Videos
                </dt>
                <dd className="text-2xl font-semibold text-gray-900">
                  {videos.length}
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <AlertTriangle className="h-6 w-6 text-red-400" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Unsafe Detected
                </dt>
                <dd className="text-2xl font-semibold text-red-600">
                  {unsafeVideos.length}
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CheckCircle className="h-6 w-6 text-green-400" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Safe Videos
                </dt>
                <dd className="text-2xl font-semibold text-green-600">
                  {safeVideos.length}
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Clock className="h-6 w-6 text-blue-400" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Processing
                </dt>
                <dd className="text-2xl font-semibold text-blue-600">
                  {processingVideos.length}
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Link
            to="/upload"
            className="flex items-center p-4 bg-primary-50 hover:bg-primary-100 rounded-lg transition-colors border border-primary-200"
          >
            <FileVideo className="h-8 w-8 text-primary-600" />
            <div className="ml-4">
              <h3 className="text-sm font-semibold text-gray-900">Upload Video</h3>
              <p className="text-xs text-gray-600">Analyze a new video file</p>
            </div>
          </Link>
          <Link
            to="/config"
            className="flex items-center p-4 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors border border-gray-200"
          >
            <TrendingUp className="h-8 w-8 text-gray-600" />
            <div className="ml-4">
              <h3 className="text-sm font-semibold text-gray-900">Configure Alerts</h3>
              <p className="text-xs text-gray-600">Set up email and SMS notifications</p>
            </div>
          </Link>
        </div>
      </div>

      {/* Recent Videos */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Recent Videos</h2>
          {videos.length > 0 && (
            <span className="text-sm text-gray-500">{videos.length} total</span>
          )}
        </div>

        {videos.length === 0 ? (
          <div className="text-center py-12">
            <FileVideo className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-sm font-medium text-gray-900 mb-2">No videos yet</h3>
            <p className="text-sm text-gray-500 mb-4">
              Upload your first video to start monitoring workplace safety
            </p>
            <Link to="/upload" className="btn-primary">
              Upload Video
            </Link>
          </div>
        ) : (
          <div className="overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Filename
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Uploaded
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {videos.map((video: any) => (
                  <tr key={video.video_id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <FileVideo className="h-5 w-5 text-gray-400 mr-3" />
                        <div className="text-sm font-medium text-gray-900">
                          {video.filename}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(video.status)}`}>
                        {getStatusIcon(video.status)}
                        <span className="ml-1">{video.status.replace('_', ' ')}</span>
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(video.uploaded_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button className="text-primary-600 hover:text-primary-900">
                        View Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

