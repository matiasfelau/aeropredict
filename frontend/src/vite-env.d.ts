/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** URL base del backend FastAPI. Por defecto http://localhost:8000 */
  readonly VITE_API_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
