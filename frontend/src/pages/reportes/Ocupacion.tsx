import { useState } from 'react'
import type { FormEvent } from 'react'

import { api } from '../../api/client'
import { Pagination } from '../../components/Pagination'
import { Card, EmptyState, ErrorMessage, Loading, OccupancyBadge } from '../../components/ui'
import { ANIO_DEFECTO, ANIOS, MESES } from '../../constants'
import { useAsync } from '../../hooks/useAsync'
import { formatNumber } from '../../utils/format'

const LIMIT = 50

export function Ocupacion() {
  const [anio, setAnio] = useState(ANIO_DEFECTO)
  const [mes, setMes] = useState(1)
  const [consulta, setConsulta] = useState({ anio: ANIO_DEFECTO, mes: 1 })
  const [offset, setOffset] = useState(0)

  const resultado = useAsync(
    () => api.reporteOcupacion(consulta.anio, consulta.mes, LIMIT, offset),
    [consulta, offset],
  )

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    setOffset(0)
    setConsulta({ anio, mes })
  }

  const items = resultado.data?.items ?? []

  return (
    <div className="report">
      <Card title="Ocupación por período">
        <form className="filters" onSubmit={handleSubmit}>
          <label className="field">
            <span>Año</span>
            <select value={anio} onChange={(e) => setAnio(Number(e.target.value))}>
              {ANIOS.map((a) => (
                <option key={a} value={a}>
                  {a}
                </option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>Mes</span>
            <select value={mes} onChange={(e) => setMes(Number(e.target.value))}>
              {MESES.map((m) => (
                <option key={m.value} value={m.value}>
                  {m.label}
                </option>
              ))}
            </select>
          </label>
          <div className="filters-actions">
            <button type="submit" className="btn btn-primary">
              Consultar
            </button>
          </div>
        </form>

        {resultado.loading ? (
          <Loading />
        ) : resultado.error ? (
          <ErrorMessage message={resultado.error} onRetry={resultado.reload} />
        ) : items.length === 0 ? (
          <EmptyState message="No hay datos para ese período." />
        ) : (
          <>
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Ruta</th>
                    <th className="num">Pasajeros</th>
                    <th className="num">Asientos</th>
                    <th className="num">Vuelos</th>
                    <th className="num">Ocupación</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((o, i) => (
                    <tr key={`${o.ruta}-${i}`}>
                      <td>{o.ruta}</td>
                      <td className="num">{formatNumber(o.pasajeros)}</td>
                      <td className="num">{formatNumber(o.asientos)}</td>
                      <td className="num">{formatNumber(o.vuelos)}</td>
                      <td className="num">
                        <OccupancyBadge factor={o.factor_ocupacion} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <Pagination
              total={resultado.data?.total ?? 0}
              limit={LIMIT}
              offset={offset}
              onChange={setOffset}
              label="rutas"
            />
          </>
        )}
      </Card>
    </div>
  )
}
