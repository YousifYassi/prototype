import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { projectApi } from '../lib/api'
import { Plus, FolderOpen, MapPin, Building2, Camera, FileVideo } from 'lucide-react'

export default function ProjectListPage() {
  const navigate = useNavigate()
  
  const { data, isLoading, error } = useQuery({
    queryKey: ['projects'],
    queryFn: projectApi.list,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading projects...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">Error loading projects. Please try again.</p>
      </div>
    )
  }

  const projects = data?.projects || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Projects</h1>
          <p className="mt-2 text-gray-600">
            Organize your safety monitoring by jurisdiction and industry
          </p>
        </div>
        <button
          onClick={() => navigate('/projects/new')}
          className="btn-primary flex items-center"
        >
          <Plus className="h-5 w-5 mr-2" />
          New Project
        </button>
      </div>

      {/* Projects Grid */}
      {projects.length === 0 ? (
        <div className="card text-center py-12">
          <FolderOpen className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No projects yet</h3>
          <p className="text-gray-600 mb-6">
            Create your first project to start monitoring workplace safety
          </p>
          <button
            onClick={() => navigate('/projects/new')}
            className="btn-primary inline-flex items-center"
          >
            <Plus className="h-5 w-5 mr-2" />
            Create Project
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project: any) => (
            <div
              key={project.id}
              onClick={() => navigate(`/projects/${project.id}`)}
              className="card hover:shadow-lg transition-shadow cursor-pointer"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">
                    {project.name}
                  </h3>
                  <div className="space-y-1 text-sm text-gray-600">
                    <div className="flex items-center">
                      <MapPin className="h-4 w-4 mr-2 text-gray-400" />
                      <span>{project.jurisdiction.name}</span>
                    </div>
                    <div className="flex items-center">
                      <Building2 className="h-4 w-4 mr-2 text-gray-400" />
                      <span>{project.industry.name}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Stats */}
              <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                <div className="flex items-center text-sm text-gray-600">
                  <Camera className="h-4 w-4 mr-1" />
                  <span>{project.stream_count} Cameras</span>
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <FileVideo className="h-4 w-4 mr-1" />
                  <span>{project.video_count} Videos</span>
                </div>
              </div>

              {/* Severity Badge */}
              <div className="mt-3">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  Min Severity: {getSeverityLabel(project.min_severity_alert)}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function getSeverityLabel(level: number): string {
  const labels: Record<number, string> = {
    1: 'Low',
    2: 'Medium',
    3: 'High',
    4: 'Critical',
    5: 'Emergency',
  }
  return labels[level] || 'Unknown'
}

