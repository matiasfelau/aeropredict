import { useState } from 'react'
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

import { api } from '../../api/client'
import { Card, EmptyState, ErrorMessage, Loading, OccupancyBadge } from '../../components/ui'
import { ANIO_DEFECTO, ANIOS, CHART_COLORS, MESES } from '../../constants'
import { useAsync } from '../../hooks/useAsync'
import { formatNumber } from '../../utils/format'

type Periodo = 'mes' | 'anio'

export function TopRutas() {
  const [periodo, setPeriodo] = useState<Periodo>('anio')
  const [anio, setAnio] = useState(ANIO_DEFECTO)
  const [mes, setMes] = useState(1)
  const [limit, setLimit] = useState(10)

  const resultado = useAsync(
    () => api.topRutas(periodo, anio, periodo === 'mes' ? mes : undefined, limit),
    [periodo, anio, mes, limit],
  )

  const chartData = (resultado.data ?? []).map((r) => ({
    ruta: r.ruta,
    pasajeros: r.pasajeros_total,
    factor: r.factor_ocupacion_promedio,
  }))

  return (
    <div className="report">
      <Card
        title="Rutas con mayor tráfico"
        actions={
          <div className="inline-fields">
            <label className="inline-field">
              <span>Período</span>
              <select value={periodo} onChange={(e) => setPeriodo(e.target.value as Periodo)}>
                <option value="anio">Anual</option>
                <option value="mes">Mensual</option>
              </select>
            </label>
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
            {periodo === 'mes' && (
              <label className="inline-field">
                <span>Mes</span>
                <select value={mes} onChange={(e) => setMes(Number(e.target.value))}>
                  {MESES.map((m) => (
                    <option key={m.value} value={m.value}>
                      {m.label}
                    </option>
                  ))}
                </select>
              </label>
            )}
            <label className="inline-field">
              <span>Top</span>
              <select value={limit} onChange={(e) => setLimit(Number(e.target.value))}>
                {[5, 10, 15, 20].map((n) => (
                  <option key={n} value={n}>
                    {n}
                  </option>
                ))}
              </select>
            </label>
          </div>
        }
      >
        {resultado.loading ? (
          <Loading />
        ) : resultado.error ? (
          <ErrorMessage message={resultado.error} onRetry={resultado.reload} />
        ) : chartData.length === 0 ? (
          <EmptyState message="No hay datos para el período seleccionado." />
        ) : (
          <>
            <ResponsiveContainer width="100%" height={Math.max(260, chartData.length * 38)}>
              <BarChart
                data={chartData}
                layout="vertical"
                margin={{ top: 8, right: 24, bottom: 8, left: 16 }}
              >
                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" tickFormatter={(v) => formatNumber(v as number)} />
                <YAxis type="category" dataKey="ruta" width={190} tick={{ fontSize: 12 }} />
                <Tooltip formatter={(value: number) => [formatNumber(value), 'Pasajeros']} />
                <Bar dataKey="pasajeros" radius={[0, 4, 4, 0]}>
                  {chartData.map((_, index) => (
                    <Cell key={index} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>

            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Ruta</th>
                    <th className="num">Pasajeros</th>
                    <th className="num">Ocupación promedio</th>
                  </tr>
                </thead>
                <tbody>
                  {(resultado.data ?? []).map((r, i) => (
                    <tr key={r.ruta}>
                      <td>{i + 1}</td>
                      <td>{r.ruta}</td>
                      <td className="num">{formatNumber(r.pasajeros_total)}</td>
                      <td className="num">
                        <OccupancyBadge factor={r.factor_ocupacion_promedio} />
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
