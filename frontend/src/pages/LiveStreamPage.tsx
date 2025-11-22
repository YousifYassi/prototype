import { useState, useEffect, useRef, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api, projectApi } from '../lib/api';
import Select, { SelectOption } from '../components/Select';

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
  project_id: number | null;
  fps: number;
}

export default function LiveStreamPage() {
  const [streams, setStreams] = useState<Stream[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [showCameraGuide, setShowCameraGuide] = useState(false);
  const [formData, setFormData] = useState<StreamFormData>({
    name: '',
    source_url: '',
    source_type: 'rtsp',
    project_id: null,
    fps: 30,
  });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Fetch projects
  const { data: projectsData } = useQuery({
    queryKey: ['projects'],
    queryFn: projectApi.list,
  });

  const projectOptions: SelectOption[] = useMemo(() => 
    projectsData?.projects.map((project: any) => ({
      value: project.id,
      label: project.name,
      description: `${project.jurisdiction.name} - ${project.industry.name}`
    })) || [],
    [projectsData]
  );

  const sourceTypeOptions: SelectOption[] = [
    { value: 'rtsp', label: 'RTSP Camera', description: 'IP cameras with RTSP protocol' },
    { value: 'rtmp', label: 'RTMP Stream', description: 'Real-Time Messaging Protocol' },
    { value: 'http', label: 'HTTP Stream', description: 'HTTP/MJPEG stream' },
    { value: 'webcam', label: 'Webcam', description: 'Local USB webcam' },
  ];

  useEffect(() => {
    loadStreams();
    // Refresh stream list every 15 seconds (reduced from 5s since we're using MJPEG streams)
    const interval = setInterval(loadStreams, 15000);
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

    // Validate project_id is set
    if (!formData.project_id) {
      setError('Please select a project');
      return;
    }

    try {
      await api.post('/streams', {
        ...formData,
        project_id: formData.project_id,
      });
      setSuccess('Stream added successfully!');
      setShowAddForm(false);
      setFormData({
        name: '',
        source_url: '',
        source_type: 'rtsp',
        project_id: null,
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
        <button
          onClick={() => setShowCameraGuide(true)}
          className="text-sm text-blue-600 hover:text-blue-700 font-medium mt-2 inline-block underline"
        >
          View detailed camera recommendations →
        </button>
      </div>

      {/* Camera Guide Modal */}
      {showCameraGuide && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            {/* Modal Header */}
            <div className="flex justify-between items-center p-6 border-b border-gray-200">
              <h2 className="text-2xl font-bold text-gray-900">
                📹 Camera Setup Guide
              </h2>
              <button
                onClick={() => setShowCameraGuide(false)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>

            {/* Modal Content */}
            <div className="overflow-y-auto p-6 space-y-6">
              {/* Requirements Section */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  Minimum Requirements
                </h3>
                <ul className="space-y-2 text-sm text-gray-700">
                  <li className="flex items-start">
                    <span className="text-blue-600 mr-2">•</span>
                    <span><strong>Resolution:</strong> 1920x1080 (1080p) or higher</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-blue-600 mr-2">•</span>
                    <span><strong>Frame Rate:</strong> 15-30 FPS minimum</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-blue-600 mr-2">•</span>
                    <span><strong>Protocols:</strong> RTSP, RTMP, or HTTP streaming support</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-blue-600 mr-2">•</span>
                    <span><strong>Network:</strong> Ethernet (preferred) or WiFi with stable connection</span>
                  </li>
                </ul>
              </div>

              {/* Budget-Friendly Options */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  Budget-Friendly Options
                </h3>
                <div className="space-y-4">
                  <div className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors">
                    <div className="mb-2">
                      <h4 className="font-semibold text-gray-900">Wyze Cam v3</h4>
                      <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded">Requires Firmware Flash</span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">
                      <strong>Resolution:</strong> 1080p @ 20 FPS | <strong>Protocol:</strong> RTSP (requires firmware)
                    </p>
                    <p className="text-sm text-gray-700 mb-2">
                      ✓ Affordable, good image quality, easy setup
                    </p>
                    
                    {/* Setup Instructions */}
                    <div className="bg-yellow-50 border border-yellow-200 rounded p-3 text-xs mb-2 space-y-2">
                      <p className="font-semibold text-yellow-900">⚠️ Setup Required (Needs microSD card):</p>
                      <ol className="list-decimal ml-4 space-y-1 text-yellow-900">
                        <li>Download legacy RTSP firmware: <a href="https://download.wyzecam.com/firmware/rtsp/demo_v3_RTSP_4.61.0.1.zip" target="_blank" rel="noopener noreferrer" className="underline text-blue-600 hover:text-blue-800">Download here</a></li>
                        <li>Extract demo_wcv3.bin to FAT32 formatted microSD card</li>
                        <li>Power off camera, insert card, hold SETUP button, power on</li>
                        <li>Hold 3-4 seconds until LED flashes purple, wait 5 min</li>
                        <li>In Wyze app: Settings → Advanced → RTSP → Enable</li>
                        <li>Set RTSP password and note camera IP address</li>
                      </ol>
                    </div>
                    
                    <p className="text-xs text-gray-500 bg-gray-50 p-2 rounded font-mono">
                      rtsp://camera-ip/live
                    </p>
                    <p className="text-xs text-gray-600 mt-1">
                      Credentials: No username, use RTSP password from step 5
                    </p>
                    <p className="text-xs text-blue-600 mt-1">
                      Best for: Small businesses, testing, single location
                    </p>
                  </div>

                  <div className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors">
                    <div className="mb-2">
                      <h4 className="font-semibold text-gray-900">Reolink E1 Pro</h4>
                      <span className="text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded">RTSP Built-in</span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">
                      <strong>Resolution:</strong> 2560x1440 @ 25 FPS | <strong>Protocol:</strong> RTSP native
                    </p>
                    <p className="text-sm text-gray-700 mb-2">
                      ✓ Good value, pan/tilt, native RTSP support
                    </p>
                    
                    {/* Setup Instructions */}
                    <div className="bg-green-50 border border-green-200 rounded p-3 text-xs mb-2 space-y-2">
                      <p className="font-semibold text-green-900">✓ Easy Setup:</p>
                      <ol className="list-decimal ml-4 space-y-1 text-green-900">
                        <li>Download Reolink app, scan QR code on camera</li>
                        <li>Connect camera to WiFi and create admin password</li>
                        <li>RTSP is enabled by default - no extra config needed</li>
                        <li>Find IP: App → Device Settings → Device Info</li>
                        <li>Use credentials: admin / your_password</li>
                      </ol>
                    </div>
                    
                    <p className="text-xs text-gray-500 bg-gray-50 p-2 rounded font-mono">
                      rtsp://admin:password@camera-ip:554/h264Preview_01_main
                    </p>
                    <p className="text-xs text-gray-600 mt-1">
                      Credentials: admin / password from setup
                    </p>
                    <p className="text-xs text-blue-600 mt-1">
                      Best for: Indoor monitoring, flexible positioning
                    </p>
                  </div>

                  <div className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors">
                    <div className="mb-2">
                      <h4 className="font-semibold text-gray-900">TP-Link Tapo C200</h4>
                      <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded">Enable RTSP Required</span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">
                      <strong>Resolution:</strong> 1080p @ 15 FPS | <strong>Protocol:</strong> RTSP (via ONVIF)
                    </p>
                    <p className="text-sm text-gray-700 mb-2">
                      ✓ Pan/tilt, motion tracking, affordable
                    </p>
                    
                    {/* Setup Instructions */}
                    <div className="bg-blue-50 border border-blue-200 rounded p-3 text-xs mb-2 space-y-2">
                      <p className="font-semibold text-blue-900">📱 Setup Steps:</p>
                      <ol className="list-decimal ml-4 space-y-1 text-blue-900">
                        <li>Download Tapo app, add camera to WiFi</li>
                        <li>Create "Camera Account" password (different from cloud password)</li>
                        <li>Enable RTSP: Settings → Advanced → Camera Account → Toggle ON</li>
                        <li>Verify username is "admin" and password is set</li>
                        <li>Find IP: Settings → Device Info → IP Address</li>
                        <li>Test with VLC before adding to system</li>
                      </ol>
                    </div>
                    
                    <p className="text-xs text-gray-500 bg-gray-50 p-2 rounded font-mono">
                      rtsp://admin:password@camera-ip:554/stream1
                    </p>
                    <p className="text-xs text-gray-600 mt-1">
                      Credentials: admin / camera account password
                    </p>
                    <p className="text-xs text-blue-600 mt-1">
                      Best for: General purpose indoor monitoring
                    </p>
                  </div>
                </div>
              </div>

              {/* Professional Options */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  Professional Options
                </h3>
                <div className="space-y-4">
                  <div className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors bg-blue-50 border-blue-200">
                    <div className="mb-2">
                      <h4 className="font-semibold text-gray-900">Hikvision DS-2CD2043G2-I</h4>
                      <span className="text-xs bg-purple-100 text-purple-800 px-2 py-0.5 rounded">Requires SADP Tool</span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">
                      <strong>Resolution:</strong> 4MP @ 30 FPS | <strong>Protocol:</strong> RTSP, ONVIF
                    </p>
                    <p className="text-sm text-gray-700 mb-2">
                      ✓ Excellent image quality, PoE, weatherproof, professional grade
                    </p>
                    
                    {/* Setup Instructions */}
                    <div className="bg-purple-50 border border-purple-200 rounded p-3 text-xs mb-2 space-y-2">
                      <p className="font-semibold text-purple-900">🔧 Professional Setup:</p>
                      <ol className="list-decimal ml-4 space-y-1 text-purple-900">
                        <li>Download SADP tool from Hikvision website</li>
                        <li>Connect camera to PoE switch, wait 2-3 minutes</li>
                        <li>Run SADP, find camera (status: INACTIVE)</li>
                        <li>Click Activate, create password (uppercase + lowercase + numbers)</li>
                        <li>Access web interface at http://camera-ip with admin/password</li>
                        <li>RTSP is enabled by default on port 554</li>
                      </ol>
                    </div>
                    
                    <p className="text-xs text-gray-500 bg-white p-2 rounded font-mono">
                      rtsp://admin:password@camera-ip:554/Streaming/Channels/101
                    </p>
                    <p className="text-xs text-gray-600 mt-1">
                      Main stream (101) = high quality, Sub stream (102) = low quality
                    </p>
                    <p className="text-xs text-blue-600 mt-1 font-medium">
                      ⭐ Recommended for: Professional installations, outdoor use
                    </p>
                  </div>

                  <div className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors">
                    <div className="mb-2">
                      <h4 className="font-semibold text-gray-900">Dahua IPC-HFW2431S-S</h4>
                      <span className="text-xs bg-indigo-100 text-indigo-800 px-2 py-0.5 rounded">ConfigTool Setup</span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">
                      <strong>Resolution:</strong> 4MP @ 30 FPS | <strong>Protocol:</strong> RTSP, ONVIF
                    </p>
                    <p className="text-sm text-gray-700 mb-2">
                      ✓ Good value, PoE, night vision, reliable
                    </p>
                    
                    {/* Setup Instructions */}
                    <div className="bg-indigo-50 border border-indigo-200 rounded p-3 text-xs mb-2 space-y-2">
                      <p className="font-semibold text-indigo-900">🔧 Setup:</p>
                      <ol className="list-decimal ml-4 space-y-1 text-indigo-900">
                        <li>Download ConfigTool from Dahua website</li>
                        <li>Connect camera to PoE, run ConfigTool → Search</li>
                        <li>Access http://camera-ip, try admin/admin</li>
                        <li>If blank password, create strong password on first login</li>
                        <li>RTSP enabled by default on port 554</li>
                        <li>Change default password immediately!</li>
                      </ol>
                    </div>
                    
                    <p className="text-xs text-gray-500 bg-gray-50 p-2 rounded font-mono">
                      rtsp://admin:password@camera-ip:554/cam/realmonitor?channel=1&subtype=0
                    </p>
                    <p className="text-xs text-gray-600 mt-1">
                      subtype=0 (main stream), subtype=1 (sub stream)
                    </p>
                    <p className="text-xs text-blue-600 mt-1">
                      Best for: 24/7 monitoring, multiple locations
                    </p>
                  </div>

                  <div className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors">
                    <div className="mb-2">
                      <h4 className="font-semibold text-gray-900">Axis M3045-V</h4>
                      <span className="text-xs bg-teal-100 text-teal-800 px-2 py-0.5 rounded">Enterprise Grade</span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">
                      <strong>Resolution:</strong> 1080p @ 30 FPS | <strong>Protocol:</strong> RTSP, ONVIF
                    </p>
                    <p className="text-sm text-gray-700 mb-2">
                      ✓ Enterprise quality, excellent low light, wide dynamic range
                    </p>
                    
                    {/* Setup Instructions */}
                    <div className="bg-teal-50 border border-teal-200 rounded p-3 text-xs mb-2 space-y-2">
                      <p className="font-semibold text-teal-900">🏢 Enterprise Setup:</p>
                      <ol className="list-decimal ml-4 space-y-1 text-teal-900">
                        <li>Download AXIS IP Utility or AXIS Device Manager</li>
                        <li>Connect camera to PoE, discover in utility</li>
                        <li>Access http://camera-ip, setup wizard starts</li>
                        <li>Create root password (uppercase + lowercase + numbers)</li>
                        <li>Best practice: Create "operator" user for RTSP (not root)</li>
                        <li>RTSP works immediately after setup</li>
                      </ol>
                    </div>
                    
                    <p className="text-xs text-gray-500 bg-gray-50 p-2 rounded font-mono">
                      rtsp://operator:password@camera-ip/axis-media/media.amp
                    </p>
                    <p className="text-xs text-gray-600 mt-1">
                      Use operator account (not root) for better security
                    </p>
                    <p className="text-xs text-blue-600 mt-1">
                      Best for: Enterprise deployments, critical applications
                    </p>
                  </div>
                </div>
              </div>

              {/* Industrial Options */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  Industrial/Enterprise Options
                </h3>
                <div className="space-y-4">
                  <div className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors">
                    <div className="mb-2">
                      <h4 className="font-semibold text-gray-900">Bosch FLEXIDOME IP 5000i</h4>
                      <span className="text-xs bg-orange-100 text-orange-800 px-2 py-0.5 rounded">Password on Label</span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">
                      <strong>Resolution:</strong> 5MP @ 30 FPS | <strong>Protocol:</strong> RTSP, ONVIF
                    </p>
                    <p className="text-sm text-gray-700 mb-2">
                      ✓ Industrial grade, intelligent video analytics, vandal-resistant
                    </p>
                    
                    {/* Setup Instructions */}
                    <div className="bg-orange-50 border border-orange-200 rounded p-3 text-xs mb-2 space-y-2">
                      <p className="font-semibold text-orange-900">🏭 Industrial Setup:</p>
                      <ol className="list-decimal ml-4 space-y-1 text-orange-900">
                        <li>Find default password on camera label/sticker</li>
                        <li>Download Bosch Configuration Manager</li>
                        <li>Connect to PoE+, scan network in tool</li>
                        <li>Access https://camera-ip (HTTPS default)</li>
                        <li>Login: service/[password from label] or user/blank</li>
                        <li>Change password immediately in Device → User Management</li>
                      </ol>
                    </div>
                    
                    <p className="text-xs text-gray-500 bg-gray-50 p-2 rounded font-mono">
                      rtsp://user:password@camera-ip/rtsp_tunnel?inst=1
                    </p>
                    <p className="text-xs text-gray-600 mt-1">
                      Check camera label for default password
                    </p>
                    <p className="text-xs text-purple-600 mt-1">
                      Best for: High-risk environments, critical infrastructure
                    </p>
                  </div>

                  <div className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors">
                    <div className="mb-2">
                      <h4 className="font-semibold text-gray-900">Avigilon H4 Multisensor</h4>
                      <span className="text-xs bg-red-100 text-red-800 px-2 py-0.5 rounded">Requires ACC Software</span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">
                      <strong>Resolution:</strong> 4x 3MP sensors | <strong>Protocol:</strong> RTSP, proprietary
                    </p>
                    <p className="text-sm text-gray-700 mb-2">
                      ✓ 360° coverage, AI analytics, exceptional quality
                    </p>
                    
                    {/* Setup Instructions */}
                    <div className="bg-red-50 border border-red-200 rounded p-3 text-xs mb-2 space-y-2">
                      <p className="font-semibold text-red-900">🎯 Advanced Setup:</p>
                      <ol className="list-decimal ml-4 space-y-1 text-red-900">
                        <li>Download Avigilon Control Center (ACC) software</li>
                        <li>Connect camera to PoE++, wait 3-5 minutes</li>
                        <li>In ACC: Add Devices → Scan network</li>
                        <li>Default: admin/admin, will force password change</li>
                        <li>Each sensor has separate RTSP stream (4 streams total)</li>
                        <li>Full features require ACC - RTSP is limited</li>
                      </ol>
                    </div>
                    
                    <p className="text-xs text-gray-500 bg-gray-50 p-2 rounded font-mono">
                      rtsp://admin:password@camera-ip/defaultPrimary?streamType=u
                    </p>
                    <p className="text-xs text-gray-600 mt-1">
                      Sensor 1-4: defaultPrimary, defaultPrimary2, defaultPrimary3, defaultPrimary4
                    </p>
                    <p className="text-xs text-purple-600 mt-1">
                      Best for: Large facilities, comprehensive coverage
                    </p>
                  </div>
                </div>
              </div>

              {/* Finding Credentials */}
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  🔑 Finding Camera Credentials
                </h3>
                <div className="space-y-3 text-sm text-gray-700">
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-1">Default Credentials:</h4>
                    <ul className="space-y-1 ml-4">
                      <li>• <strong>Wyze:</strong> No username, RTSP password (set in app)</li>
                      <li>• <strong>Reolink:</strong> admin / (your password)</li>
                      <li>• <strong>TP-Link:</strong> admin / camera account password</li>
                      <li>• <strong>Hikvision:</strong> admin / (created on activation)</li>
                      <li>• <strong>Dahua:</strong> admin / admin or (created on first login)</li>
                      <li>• <strong>Axis:</strong> root / (created on first setup)</li>
                      <li>• <strong>Bosch:</strong> service or user / (on camera label)</li>
                      <li>• <strong>Avigilon:</strong> admin / admin (force change)</li>
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-1">How to Find IP Address:</h4>
                    <ul className="space-y-1 ml-4">
                      <li>• Check camera's mobile app (Settings → Device Info)</li>
                      <li>• Use manufacturer's discovery tool (SADP, ConfigTool, etc.)</li>
                      <li>• Check your router's DHCP client list</li>
                      <li>• Use network scanner (Advanced IP Scanner, Angry IP)</li>
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-1">Testing RTSP Connection:</h4>
                    <p className="ml-4">Use VLC Media Player: Media → Open Network Stream → Enter RTSP URL</p>
                    <p className="text-xs text-gray-600 ml-4 mt-1">If video plays, your credentials and URL are correct!</p>
                  </div>
                </div>
              </div>

              {/* Setup Tips */}
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  🔒 Security Best Practices
                </h3>
                <ul className="space-y-1 text-sm text-gray-700">
                  <li>• Change default passwords immediately</li>
                  <li>• Use strong, unique passwords (16+ characters)</li>
                  <li>• Enable HTTPS for camera web interface</li>
                  <li>• Update firmware regularly</li>
                  <li>• Use VLANs to isolate cameras from main network</li>
                  <li>• Never expose cameras directly to the internet</li>
                </ul>
              </div>

              {/* Network Requirements */}
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  🌐 Network Requirements
                </h3>
                <ul className="space-y-1 text-sm text-gray-700">
                  <li>• <strong>Bandwidth per camera:</strong> 2-8 Mbps (depending on resolution)</li>
                  <li>• <strong>Recommended:</strong> Gigabit Ethernet switch</li>
                  <li>• <strong>WiFi:</strong> 5GHz preferred, strong signal required</li>
                  <li>• <strong>Latency:</strong> &lt;100ms recommended</li>
                </ul>
              </div>

              {/* Common RTSP URLs */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  Quick Reference: Common RTSP URL Formats
                </h3>
                <div className="bg-gray-900 text-gray-100 p-4 rounded-lg text-xs font-mono space-y-2">
                  <div>
                    <div className="text-gray-400 mb-1"># Hikvision</div>
                    <div>rtsp://admin:password@192.168.1.64:554/Streaming/Channels/101</div>
                  </div>
                  <div>
                    <div className="text-gray-400 mb-1"># Dahua</div>
                    <div>rtsp://admin:password@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0</div>
                  </div>
                  <div>
                    <div className="text-gray-400 mb-1"># Reolink</div>
                    <div>rtsp://admin:password@192.168.1.100:554/h264Preview_01_main</div>
                  </div>
                  <div>
                    <div className="text-gray-400 mb-1"># Axis</div>
                    <div>rtsp://root:password@192.168.1.90/axis-media/media.amp</div>
                  </div>
                  <div>
                    <div className="text-gray-400 mb-1"># TP-Link</div>
                    <div>rtsp://admin:password@192.168.1.70:554/stream1</div>
                  </div>
                  <div>
                    <div className="text-gray-400 mb-1"># Generic ONVIF</div>
                    <div>rtsp://admin:password@192.168.1.X:554/onvif1</div>
                  </div>
                </div>
              </div>
      </div>

            {/* Modal Footer */}
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
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [imageError, setImageError] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const videoRef = useRef<HTMLDivElement>(null);

  // Get auth token for MJPEG stream
  const token = localStorage.getItem('token');
  
  // Construct MJPEG stream URL with auth token
  // Add retry count to force image reload on retry
  const streamUrl = stream.status === 'active' && !imageError
    ? `http://localhost:8000/streams/${stream.stream_id}/video?token=${token}&t=${retryCount}`
    : null;
  
  // Retry connection if image fails
  const handleRetry = () => {
    setImageError(false);
    setRetryCount(prev => prev + 1);
  };

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
        {stream.status === 'active' && streamUrl && !imageError ? (
          <img
            src={streamUrl}
            alt={stream.name}
            className="w-full h-full object-contain"
            onError={() => {
              console.error('Failed to load MJPEG stream');
              setImageError(true);
            }}
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
            ) : imageError ? (
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
                <p className="mb-3">Failed to connect to stream</p>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleRetry();
                  }}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                >
                  Retry Connection
                </button>
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

