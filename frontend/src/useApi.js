import { useCallback, useEffect, useState } from 'react'
import { fetchJson } from './api.js'

// Estados: loading | error | ready. `reload` vuelve a consultar.
export function useApi(path) {
  const [state, setState] = useState({ status: 'loading', data: null, error: null })
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    const controller = new AbortController()
    fetchJson(path, { signal: controller.signal })
      .then((data) => setState({ status: 'ready', data, error: null }))
      .catch((error) => {
        if (error.name !== 'AbortError') {
          setState({ status: 'error', data: null, error: error.message })
        }
      })
    return () => controller.abort()
  }, [path, attempt])

  const reload = useCallback(() => {
    setState((prev) => ({ ...prev, status: 'loading' }))
    setAttempt((n) => n + 1)
  }, [])

  return { ...state, reload }
}
