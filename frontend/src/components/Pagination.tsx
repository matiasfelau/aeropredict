import { formatNumber } from '../utils/format'

interface PaginationProps {
  total: number
  limit: number
  offset: number
  onChange: (offset: number) => void
  /** Etiqueta del recurso paginado (ej. "rutas"). */
  label?: string
}

/** Controles de paginación basados en limit/offset (como devuelve el backend). */
export function Pagination({ total, limit, offset, onChange, label = 'resultados' }: PaginationProps) {
  const paginaActual = Math.floor(offset / limit) + 1
  const totalPaginas = Math.max(1, Math.ceil(total / limit))
  const desde = total === 0 ? 0 : offset + 1
  const hasta = Math.min(offset + limit, total)

  const irAnterior = () => onChange(Math.max(0, offset - limit))
  const irSiguiente = () => onChange(offset + limit)

  return (
    <div className="pagination">
      <span className="pagination-info">
        {formatNumber(desde)}–{formatNumber(hasta)} de {formatNumber(total)} {label}
      </span>
      <div className="pagination-controls">
        <button
          type="button"
          className="btn btn-sm"
          onClick={irAnterior}
          disabled={offset === 0}
        >
          ← Anterior
        </button>
        <span className="pagination-page">
          Página {paginaActual} / {totalPaginas}
        </span>
        <button
          type="button"
          className="btn btn-sm"
          onClick={irSiguiente}
          disabled={hasta >= total}
        >
          Siguiente →
        </button>
      </div>
    </div>
  )
}
