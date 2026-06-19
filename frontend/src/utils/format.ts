/** Funciones de formato compartidas (locale es-AR). */

const numberFormatter = new Intl.NumberFormat('es-AR')

/** 224770277 -> "224.770.277" */
export function formatNumber(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) return '—'
  return numberFormatter.format(value)
}

/** Factor de ocupación 0.847 -> "84,7%" */
export function formatPercent(factor: number | null | undefined, decimals = 1): string {
  if (factor === null || factor === undefined || Number.isNaN(factor)) return '—'
  return `${(factor * 100).toLocaleString('es-AR', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })}%`
}

const MESES = [
  'Ene',
  'Feb',
  'Mar',
  'Abr',
  'May',
  'Jun',
  'Jul',
  'Ago',
  'Sep',
  'Oct',
  'Nov',
  'Dic',
]

const MESES_LARGOS = [
  'Enero',
  'Febrero',
  'Marzo',
  'Abril',
  'Mayo',
  'Junio',
  'Julio',
  'Agosto',
  'Septiembre',
  'Octubre',
  'Noviembre',
  'Diciembre',
]

export function nombreMes(mes: number, largo = false): string {
  const idx = mes - 1
  const fuente = largo ? MESES_LARGOS : MESES
  return fuente[idx] ?? String(mes)
}

/** (2023, 10) -> "Oct 2023" */
export function formatPeriodo(anio: number, mes: number): string {
  return `${nombreMes(mes)} ${anio}`
}

/** ISO string -> "16/06/2026 14:30" */
export function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return '—'
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return '—'
  return date.toLocaleString('es-AR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/** Clasifica un factor de ocupación según los umbrales de negocio. */
export type NivelOcupacion = 'baja' | 'normal' | 'elevada'

export function nivelOcupacion(
  factor: number,
  umbralBaja = 0.6,
  umbralElevada = 0.85,
): NivelOcupacion {
  if (factor < umbralBaja) return 'baja'
  if (factor >= umbralElevada) return 'elevada'
  return 'normal'
}
