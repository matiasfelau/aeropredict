import { useState } from 'react'
import type { FormEvent } from 'react'

import { api } from '../api/client'
import type { AeropuertoFiltros } from '../api/client'
import { Pagination } from '../components/Pagination'
import { Card, EmptyState, ErrorMessage, Loading } from '../components/ui'
import { useAsync } from '../hooks/useAsync'

const LIMIT = 50

interface FormState {
  nombre: string
  localidad: string
  provincia: string
}

const EMPTY_FORM: FormState = { nombre: '', localidad: '', provincia: '' }

export function Aeropuertos() {
  const [form, setForm] = useState<FormState>(EMPTY_FORM)
  const [applied, setApplied] = useState<FormState>(EMPTY_FORM)
  const [offset, setOffset] = useState(0)

  const hayFiltros =
    applied.nombre.trim() !== '' ||
    applied.localidad.trim() !== '' ||
    applied.provincia.trim() !== ''

  const resultado = useAsync(() => {
    if (hayFiltros) {
      const filtros: AeropuertoFiltros = {
        nombre: applied.nombre.trim() || undefined,
        localidad: applied.localidad.trim() || undefined,
        provincia: applied.provincia.trim() || undefined,
        limit: LIMIT,
        offset,
      }
      return api.buscarAeropuertos(filtros)
    }
    return api.listarAeropuertos(LIMIT, offset)
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
          <h1>Aeropuertos</h1>
          <p className="page-sub">Aeropuertos geolocalizados de la red argentina.</p>
        </div>
      </div>

      <Card title="Búsqueda">
        <form className="filters" onSubmit={handleSubmit}>
          <label className="field">
            <span>Nombre</span>
            <input
              type="text"
              value={form.nombre}
              onChange={(e) => update('nombre')(e.target.value)}
              placeholder="Ej: Aeroparque"
            />
          </label>
          <label className="field">
            <span>Localidad</span>
            <input
              type="text"
              value={form.localidad}
              onChange={(e) => update('localidad')(e.target.value)}
              placeholder="Ej: Buenos Aires"
            />
          </label>
          <label className="field">
            <span>Provincia</span>
            <input
              type="text"
              value={form.provincia}
              onChange={(e) => update('provincia')(e.target.value)}
              placeholder="Ej: Córdoba"
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
      </Card>

      <Card>
        {resultado.loading ? (
          <Loading />
        ) : resultado.error ? (
          <ErrorMessage message={resultado.error} onRetry={resultado.reload} />
        ) : items.length === 0 ? (
          <EmptyState message="No se encontraron aeropuertos." />
        ) : (
          <>
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>OACI</th>
                    <th>Nombre</th>
                    <th>Localidad</th>
                    <th>Provincia</th>
                    <th>País</th>
                    <th>Coordenadas</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((a) => (
                    <tr key={a.id}>
                      <td>
                        <span className="tag tag-mono">{a.codigo_oaci}</span>
                      </td>
                      <td>{a.nombre}</td>
                      <td>{a.localidad}</td>
                      <td>{a.provincia || '—'}</td>
                      <td>{a.pais}</td>
                      <td>
                        {a.latitud != null && a.longitud != null ? (
                          <a
                            className="link"
                            href={`https://www.openstreetmap.org/?mlat=${a.latitud}&mlon=${a.longitud}#map=11/${a.latitud}/${a.longitud}`}
                            target="_blank"
                            rel="noreferrer"
                          >
                            {a.latitud.toFixed(3)}, {a.longitud.toFixed(3)} ↗
                          </a>
                        ) : (
                          '—'
                        )}
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
              label="aeropuertos"
            />
          </>
        )}
      </Card>
    </div>
  )
}
