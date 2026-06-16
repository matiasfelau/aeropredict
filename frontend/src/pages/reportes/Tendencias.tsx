import { useState } from 'react'
import type { FormEvent } from 'react'
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { api } from '../../api/client'
import { Card, EmptyState, ErrorMessage, Loading } from '../../components/ui'
import { useAsync } from '../../hooks/useAsync'
import { formatNumber, formatPeriodo } from '../../utils/format'

const OPCIONES_MESES = [6, 12, 24, 36, 48, 60]

export function Tendencias() {
  const [ruta, setRuta] = useState('')
  const [meses, setMeses] = useState(12)
  const [consulta, setConsulta] = useState<{ ruta: string; meses: number } | null>(null)

  const resultado = useAsync(() => {
    if (!consulta) return Promise.resolve([])
    return api.tendencias(consulta.ruta, consulta.meses)
  }, [consulta])

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    const limpio = ruta.trim()
    if (limpio) setConsulta({ ruta: limpio, meses })
  }

  const chartData = (resultado.data ?? []).map((t) => ({
    periodo: formatPeriodo(t.anio, t.mes),
    pasajeros: t.pasajeros,
    factor: t.factor_ocupacion,
  }))

  return (
    <div className="report">
      <Card title="Tendencia de una ruta">
        <form className="filters" onSubmit={handleSubmit}>
          <label className="field field-grow">
            <span>Ruta</span>
            <input
              type="text"
              value={ruta}
              onChange={(e) => setRuta(e.target.value)}
              placeholder="Ej: Buenos Aires - Bariloche"
            />
          </label>
          <label className="field">
            <span>Período</span>
            <select value={meses} onChange={(e) => setMeses(Number(e.target.value))}>
              {OPCIONES_MESES.map((m) => (
                <option key={m} value={m}>
                  Últimos {m} meses
                </option>
              ))}
            </select>
          </label>
          <div className="filters-actions">
            <button type="submit" className="btn btn-primary">
              Ver tendencia
            </button>
          </div>
        </form>

        {!consulta ? (
          <EmptyState message="Ingresá el nombre de una ruta para ver su evolución." />
        ) : resultado.loading ? (
          <Loading />
        ) : resultado.error ? (
          <ErrorMessage message={resultado.error} onRetry={resultado.reload} />
        ) : chartData.length === 0 ? (
          <EmptyState message="Sin datos para esa ruta." />
        ) : (
          <ResponsiveContainer width="100%" height={380}>
            <LineChart data={chartData} margin={{ top: 16, right: 24, bottom: 8, left: 8 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="periodo" tick={{ fontSize: 12 }} />
              <YAxis
                yAxisId="left"
                tickFormatter={(v) => formatNumber(v as number)}
                tick={{ fontSize: 12 }}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                domain={[0, 1]}
                tickFormatter={(v) => `${Math.round((v as number) * 100)}%`}
                tick={{ fontSize: 12 }}
              />
              <Tooltip
                formatter={(value: number, name: string) =>
                  name === 'Factor de ocupación'
                    ? [`${(value * 100).toFixed(1)}%`, name]
                    : [formatNumber(value), name]
                }
              />
              <Legend />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="pasajeros"
                name="Pasajeros"
                stroke="#1d4ed8"
                strokeWidth={2}
                dot={false}
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="factor"
                name="Factor de ocupación"
                stroke="#ea580c"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </Card>
    </div>
  )
}
