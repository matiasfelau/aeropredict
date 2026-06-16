import { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { api } from '../api/client'
import { Card, EmptyState, ErrorMessage, Loading, OccupancyBadge, StatCard } from '../components/ui'
import { ANIO_DEFECTO, ANIOS, CHART_COLORS } from '../constants'
import { useAsync } from '../hooks/useAsync'
import { formatNumber } from '../utils/format'

export function Dashboard() {
  const [anio, setAnio] = useState(ANIO_DEFECTO)

  const rutas = useAsync(() => api.listarRutas(1, 0), [])
  const aeropuertos = useAsync(() => api.listarAeropuertos(1, 0), [])
  const alertas = useAsync(() => api.alertas(500), [])
  const topRutas = useAsync(() => api.topRutas('anio', anio, undefined, 8), [anio])

  const totalAlertas = alertas.data?.length ?? null
  const alertasBajas = alertas.data?.filter((a) => a.tipo === 'baja').length ?? 0
  const alertasElevadas = alertas.data?.filter((a) => a.tipo === 'elevada').length ?? 0

  const chartData = (topRutas.data ?? []).map((r) => ({
    ruta: r.ruta,
    pasajeros: r.pasajeros_total,
    factor: r.factor_ocupacion_promedio,
  }))

  return (
    <div className="page">
      <div className="page-head">
        <div>
          <h1>Dashboard</h1>
          <p className="page-sub">Resumen de la conectividad aérea argentina (2017–2026).</p>
        </div>
      </div>

      <div className="stat-grid">
        <StatCard
          icon="🛫"
          label="Rutas registradas"
          value={rutas.loading ? '…' : formatNumber(rutas.data?.total ?? 0)}
          hint="Combinaciones de origen-destino por mes"
        />
        <StatCard
          icon="🗺️"
          label="Aeropuertos"
          value={aeropuertos.loading ? '…' : formatNumber(aeropuertos.data?.total ?? 0)}
          hint="Geolocalizados en la base"
        />
        <StatCard
          icon="🟢"
          label="Ocupación elevada"
          value={alertas.loading ? '…' : formatNumber(alertasElevadas)}
          hint="Rutas por encima del umbral (≥ 85%)"
        />
        <StatCard
          icon="🔴"
          label="Ocupación baja"
          value={alertas.loading ? '…' : formatNumber(alertasBajas)}
          hint="Rutas por debajo del umbral (< 60%)"
        />
      </div>

      <Card
        title={`Top rutas por pasajeros · ${anio}`}
        actions={
          <label className="inline-field">
            <span>Año</span>
            <select value={anio} onChange={(e) => setAnio(Number(e.target.value))}>
              {ANIOS.map((a) => (
                <option key={a} value={a}>
                  {a}
                </option>
              ))}
            </select>
          </label>
        }
      >
        {topRutas.loading ? (
          <Loading />
        ) : topRutas.error ? (
          <ErrorMessage message={topRutas.error} onRetry={topRutas.reload} />
        ) : chartData.length === 0 ? (
          <EmptyState message={`No hay datos cargados para ${anio}.`} />
        ) : (
          <ResponsiveContainer width="100%" height={360}>
            <BarChart
              data={chartData}
              layout="vertical"
              margin={{ top: 8, right: 24, bottom: 8, left: 16 }}
            >
              <CartesianGrid strokeDasharray="3 3" horizontal={false} />
              <XAxis type="number" tickFormatter={(v) => formatNumber(v as number)} />
              <YAxis type="category" dataKey="ruta" width={180} tick={{ fontSize: 12 }} />
              <Tooltip
                formatter={(value: number) => [formatNumber(value), 'Pasajeros']}
                labelStyle={{ fontWeight: 600 }}
              />
              <Bar dataKey="pasajeros" radius={[0, 4, 4, 0]}>
                {chartData.map((_, index) => (
                  <Cell key={index} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </Card>

      <Card
        title="Alertas de ocupación"
        actions={<Link to="/reportes" className="btn btn-sm btn-ghost">Ver reportes →</Link>}
      >
        {alertas.loading ? (
          <Loading />
        ) : alertas.error ? (
          <ErrorMessage message={alertas.error} onRetry={alertas.reload} />
        ) : !alertas.data || alertas.data.length === 0 ? (
          <EmptyState message="No hay alertas. ¿Cargaste los datos en el backend?" />
        ) : (
          <>
            <p className="muted">
              {formatNumber(totalAlertas ?? 0)} rutas requieren atención. Se muestran las 10
              de menor ocupación.
            </p>
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Ruta</th>
                    <th>Período</th>
                    <th>Tipo</th>
                    <th className="num">Ocupación</th>
                  </tr>
                </thead>
                <tbody>
                  {alertas.data.slice(0, 10).map((a, i) => (
                    <tr key={`${a.ruta}-${a.anio}-${a.mes}-${i}`}>
                      <td>{a.ruta}</td>
                      <td>
                        {a.mes.toString().padStart(2, '0')}/{a.anio}
                      </td>
                      <td>
                        <span className={`badge badge-${a.tipo === 'baja' ? 'baja' : 'elevada'}`}>
                          {a.tipo}
                        </span>
                      </td>
                      <td className="num">
                        <OccupancyBadge factor={a.factor_ocupacion} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </Card>
    </div>
  )
}
