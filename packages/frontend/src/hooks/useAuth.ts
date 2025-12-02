import { useState, useEffect, useCallback } from 'react'
import api from '../api/client'
import type { User, LoginRequest, Token } from '../types'

interface AuthState {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
}

export function useAuth() {
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: true,
    isAuthenticated: false,
  })

  const fetchUser = useCallback(async () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      setState({ user: null, isLoading: false, isAuthenticated: false })
      return
    }

    try {
      const response = await api.get<User>('/api/auth/me')
      setState({
        user: response.data,
        isLoading: false,
        isAuthenticated: true,
      })
    } catch {
      localStorage.removeItem('access_token')
      setState({ user: null, isLoading: false, isAuthenticated: false })
    }
  }, [])

  useEffect(() => {
    fetchUser()
  }, [fetchUser])

  const login = async (credentials: LoginRequest): Promise<void> => {
    const response = await api.post<Token>('/api/auth/login', credentials)
    localStorage.setItem('access_token', response.data.access_token)
    await fetchUser()
  }

  const logout = async (): Promise<void> => {
    try {
      await api.post('/api/auth/logout')
    } finally {
      localStorage.removeItem('access_token')
      setState({ user: null, isLoading: false, isAuthenticated: false })
    }
  }

  return {
    ...state,
    login,
    logout,
  }
}
