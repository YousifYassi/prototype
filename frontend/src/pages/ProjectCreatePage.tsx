import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { toast } from 'react-toastify'
import { projectApi, jurisdictionApi, industryApi } from '../lib/api'
import { ArrowLeft, Save, AlertCircle } from 'lucide-react'

export default function ProjectCreatePage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const [formData, setFormData] = useState({
    name: '',
    jurisdiction_id: '',
    industry_id: '',
    min_severity_alert: 1,
  })

  // Fetch jurisdictions and industries
  const { data: jurisdictionsData } = useQuery({
    queryKey: ['jurisdictions'],
    queryFn: jurisdictionApi.list,
  })

  const { data: industriesData } = useQuery({
    queryKey: ['industries'],
    queryFn: industryApi.list,
  })

  const createMutation = useMutation({
    mutationFn: projectApi.create,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      toast.success('Project created successfully!')
      navigate(`/projects/${data.project_id}`)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create project')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.name.trim()) {
      toast.error('Please enter a project name')
      return
    }

    if (!formData.jurisdiction_id) {
      toast.error('Please select a jurisdiction')
      return
    }

    if (!formData.industry_id) {
      toast.error('Please select an industry')
      return
    }

    createMutation.mutate({
      name: formData.name,
      jurisdiction_id: parseInt(formData.jurisdiction_id),
      industry_id: parseInt(formData.industry_id),
      min_severity_alert: formData.min_severity_alert,
    })
  }

  const jurisdictions = jurisdictionsData?.jurisdictions || []
  const industries = industriesData?.industries || []

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <button
          onClick={() => navigate('/projects')}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Projects
        </button>
        <h1 className="text-3xl font-bold text-gray-900">Create New Project</h1>
        <p className="mt-2 text-gray-600">
          Set up a new safety monitoring project with jurisdiction-specific regulations
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="card space-y-6">
        {/* Project Name */}
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
            Project Name *
          </label>
          <input
            type="text"
            id="name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="e.g., Main Restaurant Kitchen"
            className="input"
            required
          />
          <p className="mt-1 text-xs text-gray-500">
            Give your project a descriptive name to identify its location or purpose
          </p>
        </div>

        {/* Jurisdiction */}
        <div>
          <label htmlFor="jurisdiction" className="block text-sm font-medium text-gray-700 mb-2">
            Jurisdiction *
          </label>
          <select
            id="jurisdiction"
            value={formData.jurisdiction_id}
            onChange={(e) => setFormData({ ...formData, jurisdiction_id: e.target.value })}
            className="input"
            required
          >
            <option value="">Select a jurisdiction</option>
            {jurisdictions.map((j: any) => (
              <option key={j.id} value={j.id}>
                {j.name} ({j.country})
              </option>
            ))}
          </select>
          <p className="mt-1 text-xs text-gray-500">
            Select the legal jurisdiction for workplace safety regulations
          </p>
        </div>

        {/* Industry */}
        <div>
          <label htmlFor="industry" className="block text-sm font-medium text-gray-700 mb-2">
            Industry *
          </label>
          <select
            id="industry"
            value={formData.industry_id}
            onChange={(e) => setFormData({ ...formData, industry_id: e.target.value })}
            className="input"
            required
          >
            <option value="">Select an industry</option>
            {industries.map((i: any) => (
              <option key={i.id} value={i.id}>
                {i.name}
              </option>
            ))}
          </select>
          <p className="mt-1 text-xs text-gray-500">
            Select the industry type for specialized safety monitoring
          </p>
        </div>

        {/* Minimum Severity Alert */}
        <div>
          <label htmlFor="severity" className="block text-sm font-medium text-gray-700 mb-2">
            Minimum Alert Severity
          </label>
          <select
            id="severity"
            value={formData.min_severity_alert}
            onChange={(e) => setFormData({ ...formData, min_severity_alert: parseInt(e.target.value) })}
            className="input"
          >
            <option value="1">Low (1) - All violations</option>
            <option value="2">Medium (2) - Medium and above</option>
            <option value="3">High (3) - High and above</option>
            <option value="4">Critical (4) - Critical and emergency only</option>
            <option value="5">Emergency (5) - Emergency only</option>
          </select>
          <p className="mt-1 text-xs text-gray-500">
            Set the minimum severity level to trigger alerts and notifications
          </p>
        </div>

        {/* Info Box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start space-x-2">
            <AlertCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-1">About Projects</p>
              <p>
                Projects help you organize cameras and videos by location and industry type. 
                Each project uses jurisdiction-specific safety regulations and can have customized 
                severity thresholds for different types of violations.
              </p>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
          <button
            type="button"
            onClick={() => navigate('/projects')}
            className="btn-secondary"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={createMutation.isPending}
            className="btn-primary flex items-center disabled:opacity-50"
          >
            <Save className="h-4 w-4 mr-2" />
            {createMutation.isPending ? 'Creating...' : 'Create Project'}
          </button>
        </div>
      </form>
    </div>
  )
}

