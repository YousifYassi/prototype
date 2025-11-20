import { useState, useRef, useEffect } from 'react'
import { ChevronDown } from 'lucide-react'

/**
 * SeveritySelector - A specialized Select component for severity levels
 * 
 * This component extends the base Select pattern with colored visual indicators (chips)
 * for each severity level. It follows the same structural patterns as Select.tsx
 * for consistency across the application.
 */

interface SeveritySelectorProps {
  value: number
  onChange: (value: number) => void
  disabled?: boolean
  className?: string
}

interface SeverityOption {
  value: number
  label: string
  description: string
  color: string
}

const severityOptions: SeverityOption[] = [
  { value: 1, label: 'Low', description: 'All violations', color: 'bg-green-100 text-green-800' },
  { value: 2, label: 'Medium', description: 'Medium and above', color: 'bg-yellow-100 text-yellow-800' },
  { value: 3, label: 'High', description: 'High and above', color: 'bg-orange-100 text-orange-800' },
  { value: 4, label: 'Critical', description: 'Critical and emergency only', color: 'bg-red-100 text-red-800' },
  { value: 5, label: 'Emergency', description: 'Emergency only', color: 'bg-purple-100 text-purple-800' },
]

export default function SeveritySelector({ value, onChange, disabled = false, className = '' }: SeveritySelectorProps) {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  const selectedOption = severityOptions.find(opt => opt.value === value) || severityOptions[0]

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleSelect = (optionValue: number) => {
    onChange(optionValue)
    setIsOpen(false)
  }

  return (
    <div ref={dropdownRef} className={`relative ${className}`}>
      <button
        type="button"
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className={`w-full px-4 py-3 bg-white text-gray-900 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 border-2 border-gray-300 rounded-lg text-left ${
          disabled ? 'bg-gray-100 text-gray-500 cursor-not-allowed' : 'cursor-pointer hover:border-gray-400'
        }`}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${selectedOption.color}`}>
              {selectedOption.label}
            </span>
            <span className="text-sm text-gray-600">
              ({selectedOption.value}) - {selectedOption.description}
            </span>
          </div>
          <ChevronDown className={`h-5 w-5 text-gray-400 transition-transform ml-2 flex-shrink-0 ${isOpen ? 'rotate-180' : ''}`} />
        </div>
      </button>

      {isOpen && (
        <div className="absolute z-50 w-full mt-2 bg-white border-2 border-gray-300 rounded-lg shadow-lg max-h-80 overflow-auto">
          {severityOptions.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => handleSelect(option.value)}
              className={`w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors flex items-center space-x-3 ${
                option.value === value ? 'bg-blue-50' : ''
              }`}
            >
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${option.color}`}>
                {option.label}
              </span>
              <span className="text-sm text-gray-600">
                ({option.value}) - {option.description}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

