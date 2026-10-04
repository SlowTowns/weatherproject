// Cliente de la API. Los errores se reducen a un mensaje genérico para el usuario final;
// el detalle técnico solo se escribe en la consola del navegador.
export const GENERIC_ERROR =
  'No pudimos obtener el clima en este momento. Intenta de nuevo en unos minutos.'

export async function fetchJson(path, { signal } = {}) {
  try {
    const response = await fetch(path, { signal })
    if (!response.ok) throw new Error(`HTTP ${response.status} en ${path}`)
    return await response.json()
  } catch (error) {
    if (error.name === 'AbortError') throw error
    console.error('Error de API:', error)
    throw new Error(GENERIC_ERROR)
  }
}
