/** Piezas de UI reutilizables y de bajo nivel. */

import type { ReactNode } from 'react'

import { formatPercent, nivelOcupacion } from '../utils/format'

export function Loading({ label = 'Cargando…' }: { label?: string }) {
  return (
    <div className="loading" role="status" aria-live="polite">
      <span className="spinner" aria-hidden="true" />
      <span>{label}</span>
    </div>
  )
}

export function ErrorMessage({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="error-box" role="alert">
      <strong>Ups.</strong> {message}
      {onRetry && (
        <button type="button" className="btn btn-sm" onClick={onRetry}>
          Reintentar
        </button>
      )}
    </div>
  )
}

export function EmptyState({ message }: { message: string }) {
  return <div className="empty-state">{message}</div>
}

export function StatCard({
  label,
  value,
  hint,
  icon,
}: {
  label: string
  value: ReactNode
  hint?: string
  icon?: string
}) {
  return (
    <div className="stat-card">
      {icon && <div className="stat-icon">{icon}</div>}
      <div>
        <div className="stat-value">{value}</div>
        <div className="stat-label">{label}</div>
        {hint && <div className="stat-hint">{hint}</div>}
      </div>
    </div>
  )
}

/** Badge que colorea el factor de ocupación según los umbrales de negocio. */
export function OccupancyBadge({ factor }: { factor: number }) {
  const nivel = nivelOcupacion(factor)
  return <span className={`badge badge-${nivel}`}>{formatPercent(factor)}</span>
}

export function Card({
  title,
  children,
  actions,
}: {
  title?: ReactNode
  children: ReactNode
  actions?: ReactNode
}) {
  return (
    <section className="card">
      {(title || actions) && (
        <header className="card-header">
          {title && <h2 className="card-title">{title}</h2>}
          {actions && <div className="card-actions">{actions}</div>}
        </header>
      )}
      <div className="card-body">{children}</div>
    </section>
  )
}
