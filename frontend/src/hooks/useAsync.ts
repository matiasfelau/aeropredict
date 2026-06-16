import { useCallback, useEffect, useRef, useState } from 'react'

import { ApiError } from '../api/client'

interface AsyncState<T> {
  data: T | null
  loading: boolean
  error: string | null
}

/**
 * Ejecuta una promesa (típicamente una llamada a la API) y expone
 * { data, loading, error, reload }. Se vuelve a ejecutar cuando cambian las
 * dependencias `deps`. Ignora resultados de peticiones obsoletas.
 */
export function useAsync<T>(
  fn: () => Promise<T>,
  deps: unknown[],
): AsyncState<T> & { reload: () => void } {
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    loading: true,
    error: null,
  })
  const [nonce, setNonce] = useState(0)
  const latest = useRef(0)

  const reload = useCallback(() => setNonce((n) => n + 1), [])

  useEffect(() => {
    const callId = ++latest.current
    setState((prev) => ({ ...prev, loading: true, error: null }))

    fn()
      .then((data) => {
        if (callId === latest.current) {
          setState({ data, loading: false, error: null })
        }
      })
      .catch((err: unknown) => {
        if (callId !== latest.current) return
        const message =
          err instanceof ApiError
            ? err.message
            : err instanceof Error
              ? err.message
              : 'Error desconocido'
        setState({ data: null, loading: false, error: message })
      })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, nonce])

  return { ...state, reload }
}
