import { useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'

import { api } from '../api/client'
import type { RutaFiltros } from '../api/client'
import { Pagination } from '../components/Pagination'
import { Card, EmptyState, ErrorMessage, Loading, OccupancyBadge } from '../components/ui'
import { ANIOS, MESES } from '../constants'
import { useAsync } from '../hooks/useAsync'
import { formatNumber, formatPeriodo } from '../utils/format'

const LIMIT = 20

interface FormState {
  nombre: string
  anio: string
  mes: string
  origen: string
  destino: string
  factorMin: string
  factorMax: string
}

const EMPTY_FORM: FormState = {
  nombre: '',
  anio: '',
  mes: '',
  origen: '',
  destino: '',
  factorMin: '',
  factorMax: '',
}

function toNumber(value: string): number | undefined {
  if (value.trim() === '') return undefined
  const n = Number(value)
  return Number.isNaN(n) ? undefined : n
}

export function Rutas() {
  const navigate = useNavigate()
  const [form, setForm] = useState<FormState>(EMPTY_FORM)
  const [applied, setApplied] = useState<FormState>(EMPTY_FORM)
  const [offset, setOffset] = useState(0)

  const resultado = useAsync(() => {
    const nombre = applied.nombre.trim()
    if (nombre) {
      return api.buscarRutaPorNombre(nombre, LIMIT, offset)
    }
    const filtros: RutaFiltros = {
      anio: toNumber(applied.anio),
      mes: toNumber(applied.mes),
      origen_localidad: applied.origen.trim() || undefined,
      destino_localidad: applied.destino.trim() || undefined,
      factor_min: toNumber(applied.factorMin),
      factor_max: toNumber(applied.factorMax),
      limit: LIMIT,
      offset,
    }
    return api.buscarRutas(filtros)
  }, [applied, offset])

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    setOffset(0)
    setApplied(form)
  }

  const handleReset = () => {
    setForm(EMPTY_FORM)
    setApplied(EMPTY_FORM)
    setOffset(0)
  }

  const update = (campo: keyof FormState) => (value: string) =>
    setForm((prev) => ({ ...prev, [campo]: value }))

  const items = resultado.data?.items ?? []

  return (
    <div className="page">
      <div className="page-head">
        <div>
          <h1>Rutas</h1>
          <p className="page-sub">
            Explorá las rutas aéreas mensuales: pasajeros, asientos y factor de ocupación.
          </p>
        </div>
      </div>

      <Card title="Búsqueda">
        <form className="filters" onSubmit={handleSubmit}>
          <label className="field">
            <span>Nombre de ruta</span>
            <input
              type="text"
              value={form.nombre}
              onChange={(e) => update('nombre')(e.target.value)}
              placeholder="Ej: Bariloche"
            />
          </label>

          <label className="field">
            <span>Año</span>
            <select value={form.anio} onChange={(e) => update('anio')(e.target.value)}>
              <option value="">Todos</option>
              {ANIOS.map((a) => (
                <option key={a} value={a}>
                  {a}
                </option>
              ))}
            </select>
          </label>

          <label className="field">
            <span>Mes</span>
            <select value={form.mes} onChange={(e) => update('mes')(e.target.value)}>
              <option value="">Todos</option>
              {MESES.map((m) => (
                <option key={m.value} value={m.value}>
                  {m.label}
                </option>
              ))}
            </select>
          </label>

          <label className="field">
            <span>Origen (localidad)</span>
            <input
              type="text"
              value={form.origen}
              onChange={(e) => update('origen')(e.target.value)}
              placeholder="Ej: Buenos Aires"
            />
          </label>

          <label className="field">
            <span>Destino (localidad)</span>
            <input
              type="text"
              value={form.destino}
              onChange={(e) => update('destino')(e.target.value)}
              placeholder="Ej: Córdoba"
            />
          </label>

          <label className="field">
            <span>Factor mín. (0–1)</span>
            <input
              type="number"
              min={0}
              max={1.05}
              step={0.05}
              value={form.factorMin}
              onChange={(e) => update('factorMin')(e.target.value)}
              placeholder="0.60"
            />
          </label>

          <label className="field">
            <span>Factor máx. (0–1)</span>
            <input
              type="number"
              min={0}
              max={1.05}
              step={0.05}
              value={form.factorMax}
              onChange={(e) => update('factorMax')(e.target.value)}
              placeholder="0.85"
            />
          </label>

          <div className="filters-actions">
            <button type="submit" className="btn btn-primary">
              Buscar
            </button>
            <button type="button" className="btn btn-ghost" onClick={handleReset}>
              Limpiar
            </button>
          </div>
        </form>
        <p className="muted">
          Tip: si completás <strong>Nombre de ruta</strong>, la búsqueda usa el endpoint por
          nombre e ignora los demás filtros.
        </p>
      </Card>

      <Card>
        {resultado.loading ? (
          <Loading />
        ) : resultado.error ? (
          <ErrorMessage message={resultado.error} onRetry={resultado.reload} />
        ) : items.length === 0 ? (
          <EmptyState message="No se encontraron rutas con esos criterios." />
        ) : (
          <>
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Ruta</th>
                    <th>Período</th>
                    <th>Clasificación</th>
                    <th className="num">Pasajeros</th>
                    <th className="num">Asientos</th>
                    <th className="num">Vuelos</th>
                    <th className="num">Ocupación</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {items.map((r) => (
                    <tr
                      key={r.id}
                      className="row-clickable"
                      onClick={() => navigate(`/rutas/${r.id}`)}
                    >
                      <td>{r.ruta}</td>
                      <td>{formatPeriodo(r.anio, r.mes)}</td>
                      <td>
                        <span className="tag">{r.clasificacion_vuelo}</span>
                      </td>
                      <td className="num">{formatNumber(r.pasajeros)}</td>
                      <td className="num">{formatNumber(r.asientos)}</td>
                      <td className="num">{formatNumber(r.vuelos)}</td>
                      <td className="num">
                        <OccupancyBadge factor={r.factor_ocupacion} />
                      </td>
                      <td className="num">
                        <span className="link">Ver →</span>
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
