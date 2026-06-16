/**
 * Tipos TypeScript que reflejan los schemas Pydantic del backend
 * (`src/backend/schemas.py`). Mantener sincronizados con la API.
 */

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
}

// ---------------------------------------------------------------------------
// Rutas
// ---------------------------------------------------------------------------

export interface Ruta {
  id: number
  anio: number
  mes: number
  ruta: string
  clasificacion_vuelo: string
  origen_localidad: string
  origen_provincia: string
  destino_localidad: string
  destino_provincia: string
  pasajeros: number
  asientos: number
  vuelos: number
  factor_ocupacion: number
  creado_en: string
  actualizado_en: string
}

export interface RutaAerolinea {
  id: number
  ruta_id: number
  aerolinea: string
  pasajeros: number
  asientos: number
  vuelos: number
  factor_ocupacion: number
  creado_en: string
  actualizado_en: string
}

export interface RutaConAerolineas extends Ruta {
  rutas_aerolinea: RutaAerolinea[]
}

// ---------------------------------------------------------------------------
// Aeropuertos
// ---------------------------------------------------------------------------

export interface Aeropuerto {
  id: number
  codigo_oaci: string
  nombre: string
  localidad: string
  provincia: string
  pais: string
  latitud: number | null
  longitud: number | null
  creado_en: string
  actualizado_en: string
}

// ---------------------------------------------------------------------------
// Reportes y análisis
// ---------------------------------------------------------------------------

export interface OcupacionPorRuta {
  ruta: string
  anio: number
  mes: number
  factor_ocupacion: number
  pasajeros: number
  asientos: number
  vuelos: number
}

export interface TendenciaRuta {
  anio: number
  mes: number
  factor_ocupacion: number
  pasajeros: number
  asientos: number
}

export interface AlertaOcupacion {
  ruta: string
  tipo: 'baja' | 'elevada'
  factor_ocupacion: number
  umbral: number
  anio: number
  mes: number
}

export interface RutaTopTrafic {
  ruta: string
  pasajeros_total: number
  factor_ocupacion_promedio: number
}

export interface ParticipacionAerolinea {
  aerolinea: string
  pasajeros_total: number
  vuelos_total: number
  factor_ocupacion_promedio: number
  porcentaje_mercado: number
}

export interface ReporteCalidad {
  id: number
  fecha_generacion: string
  total_registros: number
  total_descartados: number
  rutas_unicas: number
  aerolineas_unicas: number
  periodo_inicio: string | null
  periodo_fin: string | null
}

// ---------------------------------------------------------------------------
// Admin
// ---------------------------------------------------------------------------

export interface SyncMetadata {
  ultimo_sync: string | null
  rutas_totales: number
  aeropuertos_totales: number
  reporte_calidad_mas_reciente: ReporteCalidad | null
}

export interface DataLoadResponse {
  exitoso: boolean
  timestamp: string
  rutas_nuevas: number
  rutas_actualizadas: number
  aeropuertos_nuevos: number
  aeropuertos_actualizados: number
  errores: string[]
}

// ---------------------------------------------------------------------------
// Genéricos
// ---------------------------------------------------------------------------

export interface Paginated<T> {
  total: number
  limit: number
  offset: number
  items: T[]
}
