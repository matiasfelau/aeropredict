/**
 * Cliente HTTP para la API de AeroPredict.
 *
 * - Lee la URL base desde `VITE_API_URL` (default http://localhost:8000).
 * - Adjunta el JWT (Authorization: Bearer) en los endpoints protegidos.
 * - Normaliza errores en `ApiError` con status + detalle del backend.
 */

import type {
  Aeropuerto,
  AlertaOcupacion,
  DataLoadResponse,
  OcupacionPorRuta,
  Paginated,
  ParticipacionAerolinea,
  Ruta,
  RutaConAerolineas,
  RutaTopTrafic,
  SyncMetadata,
  TendenciaRuta,
  TokenResponse,
} from './types'

export const BASE_URL = (import.meta.env.VITE_API_URL ?? 'http://localhost:8000').replace(
  /\/$/,
  '',
)

const TOKEN_KEY = 'aeropredict_token'
const USER_KEY = 'aeropredict_user'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

export function getStoredUser(): string | null {
  return localStorage.getItem(USER_KEY)
}

export function setStoredUser(username: string): void {
  localStorage.setItem(USER_KEY, username)
}

export function clearStoredUser(): void {
  localStorage.removeItem(USER_KEY)
}

/** Error con la información relevante de una respuesta fallida. */
export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

type ParamValue = string | number | boolean | undefined | null
type Params = Record<string, ParamValue>

function buildQuery(params?: Params): string {
  if (!params) return ''
  const usp = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') {
      usp.append(key, String(value))
    }
  }
  const query = usp.toString()
  return query ? `?${query}` : ''
}

interface RequestOptions {
  method?: string
  params?: Params
  body?: unknown
  auth?: boolean
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', params, body, auth = false } = options

  const headers: Record<string, string> = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (auth) {
    const token = getToken()
    if (token) headers['Authorization'] = `Bearer ${token}`
  }

  let res: Response
  try {
    res = await fetch(`${BASE_URL}${path}${buildQuery(params)}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
  } catch {
    throw new ApiError(
      0,
      `No se pudo conectar con el backend (${BASE_URL}). ¿Está corriendo el servidor FastAPI?`,
    )
  }

  if (!res.ok) {
    let detail = `Error ${res.status}`
    try {
      const data = await res.json()
      if (data && data.detail) {
        detail = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)
      }
    } catch {
      /* respuesta sin cuerpo JSON */
    }
    throw new ApiError(res.status, detail)
  }

  if (res.status === 204) return undefined as T
  return (await res.json()) as T
}

// ---------------------------------------------------------------------------
// Filtros tipados
// ---------------------------------------------------------------------------

export interface RutaFiltros {
  anio?: number
  mes?: number
  aerolinea?: string
  origen_localidad?: string
  destino_localidad?: string
  factor_min?: number
  factor_max?: number
  limit?: number
  offset?: number
}

export interface AeropuertoFiltros {
  nombre?: string
  localidad?: string
  provincia?: string
  limit?: number
  offset?: number
}

// ---------------------------------------------------------------------------
// API pública
// ---------------------------------------------------------------------------

export const api = {
  baseUrl: BASE_URL,

  // Auth -------------------------------------------------------------------
  login: (username: string, password: string) =>
    request<TokenResponse>('/auth/login', {
      method: 'POST',
      body: { username, password },
    }),

  // Rutas ------------------------------------------------------------------
  listarRutas: (limit = 20, offset = 0) =>
    request<Paginated<Ruta>>('/api/rutas', { params: { limit, offset } }),

  obtenerRuta: (id: number) => request<RutaConAerolineas>(`/api/rutas/${id}`),

  buscarRutas: (filtros: RutaFiltros) =>
    request<Paginated<Ruta>>('/api/rutas/buscar/avanzada', { params: { ...filtros } }),

  buscarRutaPorNombre: (nombre: string, limit = 20, offset = 0) =>
    request<Paginated<Ruta>>(`/api/rutas/ruta/${encodeURIComponent(nombre)}`, {
      params: { limit, offset },
    }),

  // Aeropuertos ------------------------------------------------------------
  listarAeropuertos: (limit = 50, offset = 0) =>
    request<Paginated<Aeropuerto>>('/api/aeropuertos', { params: { limit, offset } }),

  obtenerAeropuerto: (codigoOaci: string) =>
    request<Aeropuerto>(`/api/aeropuertos/${encodeURIComponent(codigoOaci)}`),

  buscarAeropuertos: (filtros: AeropuertoFiltros) =>
    request<Paginated<Aeropuerto>>('/api/aeropuertos/buscar/avanzada', {
      params: { ...filtros },
    }),

  // Reportes ---------------------------------------------------------------
  reporteOcupacion: (anio: number, mes: number, limit = 50, offset = 0) =>
    request<Paginated<OcupacionPorRuta>>('/api/reportes/ocupacion', {
      params: { anio, mes, limit, offset },
    }),

  tendencias: (ruta: string, meses = 12) =>
    request<TendenciaRuta[]>('/api/reportes/tendencias', { params: { ruta, meses } }),

  alertas: (limite = 100) =>
    request<AlertaOcupacion[]>('/api/reportes/alertas', { params: { limite } }),

  topRutas: (periodo: 'mes' | 'anio', anio: number, mes?: number, limit = 10) =>
    request<RutaTopTrafic[]>('/api/reportes/top-rutas', {
      params: { periodo, anio, mes, limit },
    }),

  participacionAerolineas: (anio: number, limit = 20) =>
    request<ParticipacionAerolinea[]>('/api/reportes/aerolineas', {
      params: { anio, limit },
    }),

  // Admin (requiere JWT) ---------------------------------------------------
  lastSync: () => request<SyncMetadata>('/admin/last-sync', { auth: true }),

  reloadData: () =>
    request<DataLoadResponse>('/admin/reload-data', { method: 'POST', auth: true }),

  // Salud ------------------------------------------------------------------
  health: () => request<{ status: string; service: string }>('/health'),
}
