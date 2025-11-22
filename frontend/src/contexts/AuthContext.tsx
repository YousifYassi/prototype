import React, { createContext, useContext, useState, useEffect, useRef, ReactNode } from 'react'
import { authApi } from '../lib/api'

interface User {
  id: string
  email: string
  name: string
  picture?: string
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (provider: string, token: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const authCheckInProgress = useRef(false)

  useEffect(() => {
    // Check if user is logged in on mount
    const checkAuth = async () => {
      // Prevent duplicate calls (React StrictMode double-invokes effects in dev)
      if (authCheckInProgress.current) return
      authCheckInProgress.current = true

      const token = localStorage.getItem('access_token')
      if (token) {
        try {
          const userData = await authApi.getMe()
          setUser(userData)
        } catch (error) {
          console.error('Auth check failed:', error)
          localStorage.removeItem('access_token')
        }
      }
      setLoading(false)
    }

    checkAuth()
  }, [])

  const login = async (provider: string, token: string) => {
    try {
      const response = await authApi.login(provider, token)
      localStorage.setItem('access_token', response.access_token)
      setUser(response.user)
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    setUser(null)
    window.location.href = '/login'
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

