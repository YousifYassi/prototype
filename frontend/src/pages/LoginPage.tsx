import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useGoogleLogin } from '@react-oauth/google'
import { toast } from 'react-toastify'
import { useAuth } from '../contexts/AuthContext'
import { Shield, AlertTriangle } from 'lucide-react'

export default function LoginPage() {
  const navigate = useNavigate()
  const { user, login } = useAuth()

  useEffect(() => {
    if (user) {
      navigate('/')
    }
  }, [user, navigate])

  const handleGoogleLogin = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      try {
        await login('google', tokenResponse.access_token)
        toast.success('Successfully logged in!')
        navigate('/')
      } catch (error) {
        console.error('Login error:', error)
        toast.error('Login failed. Please try again.')
      }
    },
    onError: () => {
      toast.error('Google login failed. Please try again.')
    },
  })

  // Facebook login handler (placeholder)
  const handleFacebookLogin = () => {
    toast.info('Facebook login coming soon! Please use Google login.')
    // TODO: Implement Facebook login when Facebook SDK is set up
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Logo and Title */}
        <div className="text-center">
          <div className="flex justify-center">
            <div className="bg-primary-600 p-3 rounded-full">
              <Shield className="h-12 w-12 text-white" />
            </div>
          </div>
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Workplace Safety Monitor
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            AI-powered unsafe action detection system
          </p>
        </div>

        {/* Login Card */}
        <div className="card mt-8">
          <div className="mb-6">
            <h3 className="text-lg font-medium text-gray-900 text-center mb-2">
              Sign in to your account
            </h3>
            <p className="text-sm text-gray-600 text-center">
              Use your Google or Facebook account to continue
            </p>
          </div>

          <div className="space-y-3">
            {/* Google Login */}
            <button
              onClick={() => handleGoogleLogin()}
              className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-all"
            >
              <svg className="h-5 w-5 mr-2" viewBox="0 0 24 24">
                <path
                  fill="#4285F4"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              Continue with Google
            </button>

            {/* Facebook Login */}
            <button
              onClick={handleFacebookLogin}
              className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-all"
            >
              <svg className="h-5 w-5 mr-2" fill="#1877F2" viewBox="0 0 24 24">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
              </svg>
              Continue with Facebook
            </button>
          </div>

          {/* Info Box */}
          <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex">
              <AlertTriangle className="h-5 w-5 text-blue-600 mr-2 flex-shrink-0" />
              <div className="text-sm text-blue-800">
                <p className="font-medium mb-1">Secure Authentication</p>
                <p className="text-blue-700">
                  We use OAuth 2.0 for secure authentication. Your credentials are never stored on our servers.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Features */}
        <div className="mt-8">
          <h4 className="text-sm font-medium text-gray-700 text-center mb-4">
            Platform Features
          </h4>
          <div className="grid grid-cols-1 gap-4">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <div className="flex items-center justify-center h-8 w-8 rounded-md bg-primary-100 text-primary-600">
                  🎥
                </div>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900">
                  Real-time Video Analysis
                </p>
                <p className="text-xs text-gray-600">
                  AI-powered detection of unsafe workplace actions
                </p>
              </div>
            </div>
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <div className="flex items-center justify-center h-8 w-8 rounded-md bg-primary-100 text-primary-600">
                  📧
                </div>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900">
                  Instant Alerts
                </p>
                <p className="text-xs text-gray-600">
                  Email and SMS notifications when unsafe actions are detected
                </p>
              </div>
            </div>
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <div className="flex items-center justify-center h-8 w-8 rounded-md bg-primary-100 text-primary-600">
                  ⚙️
                </div>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900">
                  Customizable Settings
                </p>
                <p className="text-xs text-gray-600">
                  Configure alert preferences and notification methods
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

