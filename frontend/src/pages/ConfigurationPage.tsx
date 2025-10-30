import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-toastify'
import { alertConfigApi } from '../lib/api'
import { Mail, MessageSquare, Save, Bell, CheckCircle, Shield } from 'lucide-react'

export default function ConfigurationPage() {
  const queryClient = useQueryClient()
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [enableEmail, setEnableEmail] = useState(true)
  const [enableSms, setEnableSms] = useState(false)

  const { data: config, isLoading } = useQuery({
    queryKey: ['alertConfig'],
    queryFn: alertConfigApi.get,
  })

  useEffect(() => {
    if (config) {
      setEmail(config.email || '')
      setPhone(config.phone || '')
      setEnableEmail(config.enable_email)
      setEnableSms(config.enable_sms)
    }
  }, [config])

  const updateMutation = useMutation({
    mutationFn: alertConfigApi.update,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alertConfig'] })
      toast.success('Alert configuration updated successfully!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update configuration')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    // Validate phone number format if SMS is enabled
    if (enableSms && phone && !phone.startsWith('+')) {
      toast.error('Phone number must start with + and country code (e.g., +1234567890)')
      return
    }

    updateMutation.mutate({
      email: email || undefined,
      phone: phone || undefined,
      enable_email: enableEmail,
      enable_sms: enableSms,
    })
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading configuration...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Alert Configuration</h1>
        <p className="mt-2 text-gray-600">
          Configure how you want to receive safety alerts
        </p>
      </div>

      {/* Configuration Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Email Configuration */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <Mail className="h-6 w-6 text-primary-600" />
              <h2 className="text-lg font-semibold text-gray-900">Email Alerts</h2>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={enableEmail}
                onChange={(e) => setEnableEmail(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
          </div>

          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your.email@example.com"
                className="input"
                disabled={!enableEmail}
              />
              <p className="mt-2 text-xs text-gray-500">
                Receive detailed email notifications when unsafe actions are detected
              </p>
            </div>

            {enableEmail && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start space-x-2">
                  <CheckCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div className="text-sm text-blue-800">
                    <p className="font-medium mb-1">Email notifications include:</p>
                    <ul className="list-disc list-inside space-y-1 text-blue-700">
                      <li>Type of unsafe action detected</li>
                      <li>Confidence level of detection</li>
                      <li>Video filename and timestamp</li>
                      <li>Link to saved alert clip (if available)</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* SMS Configuration */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <MessageSquare className="h-6 w-6 text-primary-600" />
              <h2 className="text-lg font-semibold text-gray-900">SMS Alerts</h2>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={enableSms}
                onChange={(e) => setEnableSms(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
          </div>

          <div className="space-y-4">
            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                Phone Number
              </label>
              <input
                type="tel"
                id="phone"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+1234567890"
                className="input"
                disabled={!enableSms}
              />
              <p className="mt-2 text-xs text-gray-500">
                Include country code (e.g., +1 for US, +44 for UK)
              </p>
            </div>

            {enableSms && (
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                <div className="flex items-start space-x-2">
                  <Bell className="h-5 w-5 text-amber-600 flex-shrink-0 mt-0.5" />
                  <div className="text-sm text-amber-800">
                    <p className="font-medium mb-1">SMS alerts are immediate</p>
                    <p className="text-amber-700">
                      Get instant text notifications for critical unsafe actions. SMS messages
                      include the action type and confidence level.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end space-x-3">
          <button
            type="submit"
            disabled={updateMutation.isPending}
            className="btn-primary flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Save className="h-4 w-4 mr-2" />
            {updateMutation.isPending ? 'Saving...' : 'Save Configuration'}
          </button>
        </div>
      </form>

      {/* Information Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="card bg-green-50 border border-green-200">
          <div className="flex items-start space-x-3">
            <Shield className="h-6 w-6 text-green-600 flex-shrink-0" />
            <div>
              <h3 className="font-semibold text-green-900 mb-2">
                Privacy & Security
              </h3>
              <p className="text-sm text-green-800">
                Your contact information is encrypted and stored securely. We only use it to
                send you safety alerts. You can update or remove it at any time.
              </p>
            </div>
          </div>
        </div>

        <div className="card bg-purple-50 border border-purple-200">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <div className="flex items-center justify-center h-6 w-6 rounded-full bg-purple-100 text-purple-600 text-xs font-bold">
                i
              </div>
            </div>
            <div>
              <h3 className="font-semibold text-purple-900 mb-2">
                Alert Frequency
              </h3>
              <p className="text-sm text-purple-800">
                To prevent notification spam, there's a cooldown period between alerts for the
                same action type. You'll receive one notification per unsafe action detected.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Setup Instructions */}
      <div className="card">
        <h3 className="font-semibold text-gray-900 mb-4">Setup Instructions</h3>
        <div className="space-y-4">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-6 h-6 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center text-sm font-bold">
              1
            </div>
            <div>
              <h4 className="text-sm font-medium text-gray-900">Configure Email</h4>
              <p className="text-sm text-gray-600">
                Enter your email address and enable email notifications to receive detailed
                alerts with detection information.
              </p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-6 h-6 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center text-sm font-bold">
              2
            </div>
            <div>
              <h4 className="text-sm font-medium text-gray-900">Add Phone Number (Optional)</h4>
              <p className="text-sm text-gray-600">
                For instant SMS alerts, enable SMS notifications and add your phone number
                with country code.
              </p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-6 h-6 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center text-sm font-bold">
              3
            </div>
            <div>
              <h4 className="text-sm font-medium text-gray-900">Save & Test</h4>
              <p className="text-sm text-gray-600">
                Click "Save Configuration" to apply your settings. Upload a test video to verify
                alerts are working correctly.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

