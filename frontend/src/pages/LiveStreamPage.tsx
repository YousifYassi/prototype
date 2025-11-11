import { useState, useEffect, useRef } from 'react';
import { api } from '../lib/api';

interface Stream {
  stream_id: string;
  name: string;
  status: string;
  source_type: string;
  fps: number;
  width: number;
  height: number;
  frame_count: number;
  error_count: number;
  last_frame_time: string | null;
  last_detection_time: string | null;
  current_result: {
    action: string;
    confidence: number;
    alert: boolean;
    is_unsafe: boolean;
  } | null;
  error_message: string | null;
}

interface StreamFormData {
  name: string;
  source_url: string;
  source_type: 'rtsp' | 'rtmp' | 'http' | 'webcam';
  fps: number;
}

export default function LiveStreamPage() {
  const [streams, setStreams] = useState<Stream[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState<StreamFormData>({
    name: '',
    source_url: '',
    source_type: 'rtsp',
    fps: 30,
  });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    loadStreams();
    // Refresh stream list every 5 seconds
    const interval = setInterval(loadStreams, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadStreams = async () => {
    try {
      const response = await api.get('/streams');
      setStreams(response.data.streams);
      setLoading(false);
    } catch (err: any) {
      console.error('Failed to load streams:', err);
      setError(err.response?.data?.detail || 'Failed to load streams');
      setLoading(false);
    }
  };

  const handleAddStream = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    try {
      await api.post('/streams', formData);
      setSuccess('Stream added successfully!');
      setShowAddForm(false);
      setFormData({
        name: '',
        source_url: '',
        source_type: 'rtsp',
        fps: 30,
      });
      loadStreams();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add stream');
    }
  };

  const handleDeleteStream = async (streamId: string) => {
    if (!confirm('Are you sure you want to stop this stream?')) return;

    try {
      await api.delete(`/streams/${streamId}`);
      setSuccess('Stream stopped successfully');
      loadStreams();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to stop stream');
    }
  };

  const getSourceTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      rtsp: 'RTSP Camera',
      rtmp: 'RTMP Stream',
      http: 'HTTP Stream',
      webcam: 'Webcam',
    };
    return labels[type] || type;
  };

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      active: 'bg-green-100 text-green-800',
      inactive: 'bg-gray-100 text-gray-800',
      error: 'bg-red-100 text-red-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Live Video Streams</h1>
          <p className="text-gray-600 mt-1">
            Monitor live camera feeds with real-time safety detection
          </p>
        </div>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          {showAddForm ? 'Cancel' : '+ Add Stream'}
        </button>
      </div>

      {/* Alert Messages */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}
      {success && (
        <div className="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg">
          {success}
        </div>
      )}

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
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., Warehouse Camera 1"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Source Type
              </label>
              <select
                value={formData.source_type}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    source_type: e.target.value as StreamFormData['source_type'],
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="rtsp">RTSP Camera</option>
                <option value="rtmp">RTMP Stream</option>
                <option value="http">HTTP Stream</option>
                <option value="webcam">Webcam</option>
              </select>
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
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
                FPS (Frames Per Second)
              </label>
              <input
                type="number"
                value={formData.fps}
                onChange={(e) =>
                  setFormData({ ...formData, fps: parseInt(e.target.value) })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                min="1"
                max="60"
                required
              />
            </div>

            <div className="flex gap-2">
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Add Stream
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
        <a
          href="#camera-guide"
          className="text-sm text-blue-600 hover:text-blue-700 font-medium mt-2 inline-block"
        >
          View detailed camera recommendations →
        </a>
      </div>

      {/* Active Streams */}
      {streams.length === 0 ? (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <div className="text-gray-400 mb-4">
            <svg
              className="w-16 h-16 mx-auto"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
              />
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            No active streams
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
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {streams.map((stream) => (
            <StreamCard
              key={stream.stream_id}
              stream={stream}
              onDelete={handleDeleteStream}
              getStatusBadge={getStatusBadge}
              getSourceTypeLabel={getSourceTypeLabel}
            />
          ))}
        </div>
      )}
    </div>
  );
}

interface StreamCardProps {
  stream: Stream;
  onDelete: (streamId: string) => void;
  getStatusBadge: (status: string) => string;
  getSourceTypeLabel: (type: string) => string;
}

function StreamCard({
  stream,
  onDelete,
  getStatusBadge,
  getSourceTypeLabel,
}: StreamCardProps) {
  const [frameData, setFrameData] = useState<string | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const videoRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (stream.status !== 'active') return;

    // Poll for frames every 100ms
    const interval = setInterval(async () => {
      try {
        const response = await api.get(`/streams/${stream.stream_id}/frame`);
        setFrameData(response.data.frame);
      } catch (err) {
        console.error('Failed to fetch frame:', err);
      }
    }, 100);

    return () => clearInterval(interval);
  }, [stream.stream_id, stream.status]);

  const toggleFullscreen = () => {
    if (!videoRef.current) return;

    if (!isFullscreen) {
      if (videoRef.current.requestFullscreen) {
        videoRef.current.requestFullscreen();
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
    setIsFullscreen(!isFullscreen);
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      {/* Video Display */}
      <div
        ref={videoRef}
        className="relative bg-gray-900 aspect-video cursor-pointer"
        onClick={toggleFullscreen}
      >
        {stream.status === 'active' && frameData ? (
          <img
            src={`data:image/jpeg;base64,${frameData}`}
            alt={stream.name}
            className="w-full h-full object-contain"
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center text-gray-400">
            {stream.status === 'error' ? (
              <div className="text-center">
                <svg
                  className="w-12 h-12 mx-auto mb-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <p>Stream Error</p>
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
          <div className="absolute top-4 left-4 bg-red-600 text-white px-3 py-1 rounded-lg font-semibold animate-pulse">
            ⚠️ UNSAFE ACTION DETECTED
          </div>
        )}
      </div>

      {/* Stream Info */}
      <div className="p-4">
        <div className="flex justify-between items-start mb-3">
          <div>
            <h3 className="font-semibold text-lg text-gray-900">{stream.name}</h3>
            <p className="text-sm text-gray-500">
              {getSourceTypeLabel(stream.source_type)}
            </p>
          </div>
          <span
            className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadge(
              stream.status
            )}`}
          >
            {stream.status}
          </span>
        </div>

        {/* Current Detection */}
        {stream.current_result && (
          <div className="mb-3 p-3 bg-gray-50 rounded-lg">
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

        {/* Stream Stats */}
        <div className="grid grid-cols-2 gap-3 text-sm mb-3">
          <div>
            <span className="text-gray-600">Resolution:</span>
            <span className="ml-1 font-medium">
              {stream.width}x{stream.height}
            </span>
          </div>
          <div>
            <span className="text-gray-600">FPS:</span>
            <span className="ml-1 font-medium">{stream.fps}</span>
          </div>
          <div>
            <span className="text-gray-600">Frames:</span>
            <span className="ml-1 font-medium">{stream.frame_count}</span>
          </div>
          <div>
            <span className="text-gray-600">Errors:</span>
            <span className="ml-1 font-medium">{stream.error_count}</span>
          </div>
        </div>

        {/* Error Message */}
        {stream.error_message && (
          <div className="mb-3 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-800">
            {stream.error_message}
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-2">
          <button
            onClick={toggleFullscreen}
            className="flex-1 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
          >
            Fullscreen
          </button>
          <button
            onClick={() => onDelete(stream.stream_id)}
            className="px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm"
          >
            Stop
          </button>
        </div>
      </div>
    </div>
  );
}

