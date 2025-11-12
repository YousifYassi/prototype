import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate, Link } from 'react-router-dom'
import { toast } from 'react-toastify'
import { videoApi } from '../lib/api'
import { Upload, FileVideo, X, CheckCircle, AlertCircle } from 'lucide-react'

export default function VideoUploadPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [dragActive, setDragActive] = useState(false)

  const uploadMutation = useMutation({
    mutationFn: videoApi.upload,
    onSuccess: (data) => {
      toast.success('Video uploaded successfully! Processing in background...')
      setSelectedFile(null)
      queryClient.invalidateQueries({ queryKey: ['videos'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Upload failed. Please try again.')
    },
  })

  const resetState = () => {
    setSelectedFile(null)
    uploadMutation.reset()
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0]
      if (file.type.startsWith('video/')) {
        setSelectedFile(file)
        if (uploadMutation.isSuccess || uploadMutation.isError) {
          uploadMutation.reset()
        }
      } else {
        toast.error('Please select a video file')
      }
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      if (file.type.startsWith('video/')) {
        setSelectedFile(file)
        if (uploadMutation.isSuccess || uploadMutation.isError) {
          uploadMutation.reset()
        }
      } else {
        toast.error('Please select a video file')
      }
    }
  }

  const handleUpload = () => {
    if (selectedFile) {
      uploadMutation.mutate(selectedFile)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Upload Video</h1>
        <p className="mt-2 text-gray-600">
          Upload a video file to analyze for unsafe workplace actions
        </p>
      </div>

      {/* Upload Section */}
      <div className="card">
        {!selectedFile ? (
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
              dragActive
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-300 hover:border-primary-400'
            }`}
          >
            <input
              type="file"
              id="video-upload"
              accept="video/*"
              onChange={handleFileChange}
              className="hidden"
            />
            <label htmlFor="video-upload" className="cursor-pointer">
              <Upload className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-4 text-lg font-medium text-gray-900">
                Upload a video
              </h3>
              <p className="mt-2 text-sm text-gray-600">
                Drag and drop or click to select
              </p>
              <p className="mt-1 text-xs text-gray-500">
                Supports: MP4, AVI, MOV, WebM (max 500MB)
              </p>
              <button
                type="button"
                className="mt-6 btn-primary"
                onClick={() => document.getElementById('video-upload')?.click()}
              >
                Select Video
              </button>
            </label>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Selected File Info */}
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <FileVideo className="h-10 w-10 text-primary-600" />
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {selectedFile.name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {formatFileSize(selectedFile.size)}
                  </p>
                </div>
              </div>
              <button
                onClick={resetState}
                className="text-gray-400 hover:text-gray-600"
                disabled={uploadMutation.isPending}
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Upload Status */}
            {uploadMutation.isPending && (
              <div className="flex items-center space-x-3 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-600"></div>
                <span className="text-sm text-blue-900">Uploading video...</span>
              </div>
            )}

            {uploadMutation.isSuccess && (
              <div className="flex flex-col space-y-3 p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center space-x-3">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span className="text-sm text-green-900">
                    Upload successful! Processing has started in the background.
                  </span>
                </div>
                <p className="text-xs text-green-800">
                  You can stay here to upload another video or return to the dashboard to monitor progress.
                </p>
                <div className="flex flex-col sm:flex-row sm:items-center sm:space-x-2 space-y-2 sm:space-y-0">
                  <button
                    type="button"
                    onClick={resetState}
                    className="btn-secondary text-sm"
                  >
                    Upload Another Video
                  </button>
                  <button
                    type="button"
                    onClick={() => navigate('/')}
                    className="btn-primary text-sm"
                  >
                    Go to Dashboard
                  </button>
                </div>
              </div>
            )}

            {uploadMutation.isError && (
              <div className="flex items-center space-x-3 p-4 bg-red-50 border border-red-200 rounded-lg">
                <AlertCircle className="h-5 w-5 text-red-600" />
                <span className="text-sm text-red-900">
                  Upload failed. Please try again.
                </span>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex space-x-3">
              <button
                onClick={handleUpload}
                disabled={uploadMutation.isPending}
                className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {uploadMutation.isPending ? 'Uploading...' : 'Upload & Analyze'}
              </button>
              <button
                onClick={resetState}
                disabled={uploadMutation.isPending}
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Info Boxes */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="card bg-blue-50 border border-blue-200">
          <h3 className="font-semibold text-blue-900 mb-2">
            What happens after upload?
          </h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Video is processed frame-by-frame using AI</li>
            <li>• Unsafe actions are detected automatically</li>
            <li>• Results available in a few minutes</li>
            <li>• You'll receive alerts if unsafe actions found</li>
          </ul>
        </div>

        <div className="card bg-amber-50 border border-amber-200">
          <h3 className="font-semibold text-amber-900 mb-2">
            Detected Unsafe Actions
          </h3>
          <ul className="text-sm text-amber-800 space-y-1">
            <li>• Aggressive driving</li>
            <li>• Distracted behavior</li>
            <li>• Unsafe lane changes</li>
            <li>• Running red lights</li>
            <li>• And more...</li>
          </ul>
        </div>
      </div>

      {/* Live Stream Feature */}
      <div className="card bg-purple-50 border border-purple-200">
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            <div className="flex items-center justify-center h-10 w-10 rounded-full bg-purple-100 text-purple-600">
              📹
            </div>
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-purple-900 mb-1">
              Live Stream Monitoring Available!
            </h3>
            <p className="text-sm text-purple-800 mb-3">
              Monitor live camera feeds with real-time AI detection. Connect IP cameras, RTSP streams, or webcams for continuous workplace safety monitoring.
            </p>
            <Link 
              to="/streams"
              className="inline-flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm font-medium"
            >
              Go to Live Streams
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

