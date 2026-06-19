import { useEffect, useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'

import { api, BASE_URL } from '../api/client'
import { useAuth } from '../context/AuthContext'

type BackendStatus = 'checking' | 'online' | 'offline'

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: '📊', end: true },
  { to: '/rutas', label: 'Rutas', icon: '🛫', end: false },
  { to: '/aeropuertos', label: 'Aeropuertos', icon: '🗺️', end: false },
  { to: '/reportes', label: 'Reportes', icon: '📈', end: false },
  { to: '/admin', label: 'Admin', icon: '⚙️', end: false },
]

function BackendIndicator() {
  const [status, setStatus] = useState<BackendStatus>('checking')

  useEffect(() => {
    let activo = true
    api
      .health()
      .then(() => activo && setStatus('online'))
      .catch(() => activo && setStatus('offline'))
    return () => {
      activo = false
    }
  }, [])

  const texto =
    status === 'online' ? 'Backend conectado' : status === 'offline' ? 'Backend sin conexión' : 'Verificando…'

  return (
    <div className={`backend-status backend-${status}`} title={BASE_URL}>
      <span className="status-dot" aria-hidden="true" />
      {texto}
    </div>
  )
}

export function Layout() {
  const { isAuthenticated, username, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-logo" aria-hidden="true">
            ✈️
          </span>
          <div>
            <div className="brand-name">AeroPredict</div>
            <div className="brand-sub">Argentina</div>
          </div>
        </div>

        <nav className="nav">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
            >
              <span className="nav-icon" aria-hidden="true">
                {item.icon}
              </span>
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <BackendIndicator />
        </div>
      </aside>

      <div className="main">
        <header className="topbar">
          <div className="topbar-spacer" />
          {isAuthenticated ? (
            <div className="user-box">
              <span className="user-name">👤 {username}</span>
              <button type="button" className="btn btn-sm btn-ghost" onClick={handleLogout}>
                Salir
              </button>
            </div>
          ) : (
            <button
              type="button"
              className="btn btn-sm"
              onClick={() => navigate('/login')}
            >
              Iniciar sesión
            </button>
          )}
        </header>

        <main className="content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
