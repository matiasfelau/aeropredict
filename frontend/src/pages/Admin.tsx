import { useState } from 'react'

import { api, ApiError } from '../api/client'
import { useAuth } from '../context/AuthContext'
import { Card, EmptyState, ErrorMessage, Loading, StatCard } from '../components/ui'
import { useAsync } from '../hooks/useAsync'
import type { DataLoadResponse } from '../api/types'
import { formatDateTime, formatNumber } from '../utils/format'

export function Admin() {
  const { logout } = useAuth()
  const sync = useAsync(() => api.lastSync(), [])

  const [recargando, setRecargando] = useState(false)
  const [resultado, setResultado] = useState<DataLoadResponse | null>(null)
  const [errorRecarga, setErrorRecarga] = useState<string | null>(null)

  const handleReload = async () => {
    setRecargando(true)
    setErrorRecarga(null)
    setResultado(null)
    try {
      const res = await api.reloadData()
      setResultado(res)
      sync.reload()
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        setErrorRecarga('Tu sesión expiró. Volvé a iniciar sesión.')
        logout()
      } else if (err instanceof ApiError) {
        setErrorRecarga(err.message)
      } else {
        setErrorRecarga('No se pudo recargar los datos.')
      }
    } finally {
      setRecargando(false)
    }
  }

  const reporte = sync.data?.reporte_calidad_mas_reciente ?? null

  return (
    <div className="page">
      <div className="page-head">
        <div>
          <h1>Administración</h1>
          <p className="page-sub">Estado del pipeline ETL y sincronización de datos.</p>
        </div>
      </div>

      <Card title="Último sync con el pipeline">
        {sync.loading ? (
          <Loading />
        ) : sync.error ? (
          <ErrorMessage message={sync.error} onRetry={sync.reload} />
        ) : !sync.data ? (
          <EmptyState message="Sin metadata disponible." />
        ) : (
          <>
            <div className="stat-grid">
              <StatCard
                icon="🛫"
                label="Rutas en la base"
                value={formatNumber(sync.data.rutas_totales)}
              />
              <StatCard
                icon="🗺️"
                label="Aeropuertos en la base"
                value={formatNumber(sync.data.aeropuertos_totales)}
              />
              <StatCard
                icon="🕑"
                label="Último sync"
                value={formatDateTime(sync.data.ultimo_sync)}
              />
            </div>

            {reporte && (
              <div className="kv-grid kv-grid-wide">
                <div>
                  <div className="kv-label">Registros procesados</div>
                  <div className="kv-value">{formatNumber(reporte.total_registros)}</div>
                </div>
                <div>
                  <div className="kv-label">Descartados</div>
                  <div className="kv-value">{formatNumber(reporte.total_descartados)}</div>
                </div>
                <div>
                  <div className="kv-label">Rutas únicas</div>
                  <div className="kv-value">{formatNumber(reporte.rutas_unicas)}</div>
                </div>
                <div>
                  <div className="kv-label">Aerolíneas únicas</div>
                  <div className="kv-value">{formatNumber(reporte.aerolineas_unicas)}</div>
                </div>
                <div>
                  <div className="kv-label">Período</div>
                  <div className="kv-value">
                    {reporte.periodo_inicio ?? '—'} → {reporte.periodo_fin ?? '—'}
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </Card>

      <Card title="Recargar datos desde los CSV del pipeline">
        <p className="muted">
          Ejecuta <code>POST /admin/reload-data</code>: vuelve a leer los archivos procesados
          (<code>base_mensual_ruta.csv</code>, etc.) y hace upsert en la base.
        </p>
        <button
          type="button"
          className="btn btn-primary"
          onClick={handleReload}
          disabled={recargando}
        >
          {recargando ? 'Recargando…' : 'Recargar datos'}
        </button>

        {errorRecarga && <ErrorMessage message={errorRecarga} />}

        {resultado && (
          <div className="reload-result">
            <p className={resultado.exitoso ? 'success-text' : 'error-text'}>
              {resultado.exitoso ? '✅ Carga completada' : '⚠️ Carga con observaciones'} ·{' '}
              {formatDateTime(resultado.timestamp)}
            </p>
            <div className="stat-grid">
              <StatCard label="Rutas nuevas" value={formatNumber(resultado.rutas_nuevas)} />
              <StatCard
                label="Rutas actualizadas"
                value={formatNumber(resultado.rutas_actualizadas)}
              />
              <StatCard
                label="Aeropuertos nuevos"
                value={formatNumber(resultado.aeropuertos_nuevos)}
              />
              <StatCard
                label="Aeropuertos actualizados"
                value={formatNumber(resultado.aeropuertos_actualizados)}
              />
            </div>
            {resultado.errores.length > 0 && (
              <ul className="error-list">
                {resultado.errores.map((e, i) => (
                  <li key={i}>{e}</li>
                ))}
              </ul>
            )}
          </div>
        )}
      </Card>
    </div>
  )
}
