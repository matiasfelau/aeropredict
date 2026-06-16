import { Link, useParams } from 'react-router-dom'
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'

import { api } from '../api/client'
import { Card, EmptyState, ErrorMessage, Loading, OccupancyBadge, StatCard } from '../components/ui'
import { CHART_COLORS } from '../constants'
import { useAsync } from '../hooks/useAsync'
import { formatNumber, formatPeriodo } from '../utils/format'

export function RutaDetalle() {
  const { id } = useParams<{ id: string }>()
  const rutaId = Number(id)

  const { data, loading, error, reload } = useAsync(
    () => api.obtenerRuta(rutaId),
    [rutaId],
  )

  if (Number.isNaN(rutaId)) {
    return (
      <div className="page">
        <ErrorMessage message="ID de ruta inválido." />
      </div>
    )
  }

  return (
    <div className="page">
      <div className="breadcrumb">
        <Link to="/rutas">← Volver a rutas</Link>
      </div>

      {loading ? (
        <Loading />
      ) : error ? (
        <ErrorMessage message={error} onRetry={reload} />
      ) : !data ? (
        <EmptyState message="Ruta no encontrada." />
      ) : (
        <>
          <div className="page-head">
            <div>
              <h1>{data.ruta}</h1>
              <p className="page-sub">
                {formatPeriodo(data.anio, data.mes)} · {data.clasificacion_vuelo}
              </p>
            </div>
          </div>

          <div className="stat-grid">
            <StatCard icon="👥" label="Pasajeros" value={formatNumber(data.pasajeros)} />
            <StatCard icon="💺" label="Asientos" value={formatNumber(data.asientos)} />
            <StatCard icon="🛬" label="Vuelos" value={formatNumber(data.vuelos)} />
            <StatCard
              icon="📊"
              label="Factor de ocupación"
              value={<OccupancyBadge factor={data.factor_ocupacion} />}
            />
          </div>

          <Card title="Origen y destino">
            <div className="kv-grid">
              <div>
                <div className="kv-label">Origen</div>
                <div className="kv-value">{data.origen_localidad}</div>
                <div className="kv-sub">{data.origen_provincia || '—'}</div>
              </div>
              <div className="kv-arrow" aria-hidden="true">
                ✈️ →
              </div>
              <div>
                <div className="kv-label">Destino</div>
                <div className="kv-value">{data.destino_localidad}</div>
                <div className="kv-sub">{data.destino_provincia || '—'}</div>
              </div>
            </div>
          </Card>

          <Card title="Desglose por aerolínea">
            {data.rutas_aerolinea.length === 0 ? (
              <EmptyState message="Sin desglose por aerolínea para esta ruta." />
            ) : (
              <div className="split">
                <div className="split-chart">
                  <ResponsiveContainer width="100%" height={280}>
                    <PieChart>
                      <Pie
                        data={data.rutas_aerolinea}
                        dataKey="pasajeros"
                        nameKey="aerolinea"
                        cx="50%"
                        cy="50%"
                        outerRadius={100}
                        label={(entry) => entry.aerolinea}
                      >
                        {data.rutas_aerolinea.map((_, index) => (
                          <Cell key={index} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value: number) => formatNumber(value)} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="split-table table-wrap">
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Aerolínea</th>
                        <th className="num">Pasajeros</th>
                        <th className="num">Vuelos</th>
                        <th className="num">Ocupación</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.rutas_aerolinea.map((a) => (
                        <tr key={a.id}>
                          <td>{a.aerolinea}</td>
                          <td className="num">{formatNumber(a.pasajeros)}</td>
                          <td className="num">{formatNumber(a.vuelos)}</td>
                          <td className="num">
                            <OccupancyBadge factor={a.factor_ocupacion} />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </Card>
        </>
      )}
    </div>
  )
}
