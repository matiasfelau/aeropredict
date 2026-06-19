/** Constantes de dominio compartidas por las páginas. */

// El dataset abarca 2017-01 → 2026-04 (ver README del módulo de datos).
const ANIO_INICIAL = 2017
const ANIO_FINAL = 2026

export const ANIOS: number[] = Array.from(
  { length: ANIO_FINAL - ANIO_INICIAL + 1 },
  (_, i) => ANIO_FINAL - i,
)

export const MESES: { value: number; label: string }[] = [
  { value: 1, label: 'Enero' },
  { value: 2, label: 'Febrero' },
  { value: 3, label: 'Marzo' },
  { value: 4, label: 'Abril' },
  { value: 5, label: 'Mayo' },
  { value: 6, label: 'Junio' },
  { value: 7, label: 'Julio' },
  { value: 8, label: 'Agosto' },
  { value: 9, label: 'Septiembre' },
  { value: 10, label: 'Octubre' },
  { value: 11, label: 'Noviembre' },
  { value: 12, label: 'Diciembre' },
]

/** Año por defecto para los reportes (último con cobertura completa de meses). */
export const ANIO_DEFECTO = 2024

/** Paleta usada en los gráficos. */
export const CHART_COLORS = [
  '#1d4ed8',
  '#0891b2',
  '#7c3aed',
  '#db2777',
  '#ea580c',
  '#16a34a',
  '#ca8a04',
  '#dc2626',
  '#0d9488',
  '#4f46e5',
]
