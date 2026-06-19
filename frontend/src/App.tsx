import { Navigate, Route, Routes } from 'react-router-dom'

import { Layout } from './components/Layout'
import { ProtectedRoute } from './components/ProtectedRoute'
import { Admin } from './pages/Admin'
import { Aeropuertos } from './pages/Aeropuertos'
import { Dashboard } from './pages/Dashboard'
import { Login } from './pages/Login'
import { NotFound } from './pages/NotFound'
import { Reportes } from './pages/Reportes'
import { RutaDetalle } from './pages/RutaDetalle'
import { Rutas } from './pages/Rutas'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="rutas" element={<Rutas />} />
        <Route path="rutas/:id" element={<RutaDetalle />} />
        <Route path="aeropuertos" element={<Aeropuertos />} />
        <Route path="reportes" element={<Reportes />} />
        <Route
          path="admin"
          element={
            <ProtectedRoute>
              <Admin />
            </ProtectedRoute>
          }
        />
        <Route path="404" element={<NotFound />} />
        <Route path="*" element={<Navigate to="/404" replace />} />
      </Route>
    </Routes>
  )
}
