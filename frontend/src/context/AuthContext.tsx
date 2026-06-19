import { createContext, useCallback, useContext, useMemo, useState } from 'react'
import type { ReactNode } from 'react'

import {
  api,
  clearStoredUser,
  clearToken,
  getStoredUser,
  getToken,
  setStoredUser,
  setToken,
} from '../api/client'

interface AuthContextValue {
  username: string | null
  isAuthenticated: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [username, setUsername] = useState<string | null>(() => getStoredUser())
  const [token, setTokenState] = useState<string | null>(() => getToken())

  const login = useCallback(async (user: string, password: string) => {
    const res = await api.login(user, password)
    setToken(res.access_token)
    setStoredUser(user)
    setTokenState(res.access_token)
    setUsername(user)
  }, [])

  const logout = useCallback(() => {
    clearToken()
    clearStoredUser()
    setTokenState(null)
    setUsername(null)
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({
      username,
      isAuthenticated: Boolean(token),
      login,
      logout,
    }),
    [username, token, login, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth debe usarse dentro de <AuthProvider>')
  }
  return ctx
}
