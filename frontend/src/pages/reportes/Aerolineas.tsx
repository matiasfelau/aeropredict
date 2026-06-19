import { useState } from 'react'
import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'

import { api } from '../../api/client'
import { Card, EmptyState, ErrorMessage, Loading, OccupancyBadge } from '../../components/ui'
import { ANIO_DEFECTO, ANIOS, CHART_COLORS } from '../../constants'
import { useAsync } from '../../hooks/useAsync'
import { formatNumber, formatPercent } from '../../utils/format'

export function Aerolineas() {
  const [anio, setAnio] = useState(ANIO_DEFECTO)

  const resultado = useAsync(() => api.participacionAerolineas(anio, 20), [anio])

  const data = resultado.data ?? []
  const chartData = data.slice(0, 8).map((a) => ({
    aerolinea: a.aerolinea,
    valor: a.porcentaje_mercado,
  }))

  return (
    <div className="report">
      <Card
        title={`Participación de mercado por aerolínea · ${anio}`}
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
        {resultado.loading ? (
          <Loading />
        ) : resultado.error ? (
          <ErrorMessage message={resultado.error} onRetry={resultado.reload} />
        ) : data.length === 0 ? (
          <EmptyState message="No hay datos de aerolíneas para ese año." />
        ) : (
          <div className="split">
            <div className="split-chart">
              <ResponsiveContainer width="100%" height={320}>
                <PieChart>
                  <Pie
                    data={chartData}
                    dataKey="valor"
                    nameKey="aerolinea"
                    cx="50%"
                    cy="50%"
                    outerRadius={110}
                    label={(entry) => `${(entry.valor as number).toFixed(0)}%`}
                  >
                    {chartData.map((_, index) => (
                      <Cell key={index} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => `${value.toFixed(1)}%`} />
                  <Legend />
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
                    <th className="num">Mercado</th>
                  </tr>
                </thead>
                <tbody>
                  {data.map((a) => (
                    <tr key={a.aerolinea}>
                      <td>{a.aerolinea}</td>
                      <td className="num">{formatNumber(a.pasajeros_total)}</td>
                      <td className="num">{formatNumber(a.vuelos_total)}</td>
                      <td className="num">
                        <OccupancyBadge factor={a.factor_ocupacion_promedio} />
                      </td>
                      <td className="num">{formatPercent(a.porcentaje_mercado / 100)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </Card>
    </div>
  )
}
