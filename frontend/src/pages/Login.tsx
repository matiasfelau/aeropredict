import { useState } from 'react'
import type { FormEvent } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

import { ApiError } from '../api/client'
import { useAuth } from '../context/AuthContext'

interface LocationState {
  from?: string
}

export function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const from = (location.state as LocationState | null)?.from ?? '/admin'

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      await login(username.trim(), password)
      navigate(from, { replace: true })
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        setError('Usuario o contraseña incorrectos.')
      } else if (err instanceof ApiError) {
        setError(err.message)
      } else {
        setError('No se pudo iniciar sesión.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-brand">
          <span aria-hidden="true">✈️</span>
          <h1>AeroPredict</h1>
          <p>Panel de análisis de conectividad aérea de Argentina</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <label className="field">
            <span>Usuario</span>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              required
              minLength={3}
              placeholder="admin"
            />
          </label>

          <label className="field">
            <span>Contraseña</span>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
              minLength={6}
              placeholder="••••••••"
            />
          </label>

          {error && (
            <div className="error-box" role="alert">
              {error}
            </div>
          )}

          <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
            {loading ? 'Ingresando…' : 'Iniciar sesión'}
          </button>
        </form>

        <p className="login-hint">
          La autenticación solo es necesaria para la sección <strong>Admin</strong>. El
          resto del panel (rutas, aeropuertos y reportes) es de consulta libre.
        </p>
        <button type="button" className="btn btn-ghost btn-block" onClick={() => navigate('/')}>
          ← Volver al dashboard
        </button>
      </div>
    </div>
  )
}
