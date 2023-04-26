let _apiUrl =
  localStorage.getItem('apiUrl') ??
  `${window.location.protocol}//${window.location.host}/api`

export const apiUrl = _apiUrl

export const setApiUrl = (url: string) => {
  _apiUrl = url
  localStorage.setItem('apiUrl', url)
}

export const checkApiUrl = async (count: number = 0) => {
  if (count > 3) {
    return false
  }
  try {
    const res = await fetch(`${apiUrl}/status`)
    if (res.ok) {
      return true
    }
  } catch (e) {
    console.error(e)
  }
  _apiUrl = prompt('API URL', _apiUrl)
  return checkApiUrl(count + 1)
}

export const getLights = async () => {
  const res = await fetch(`${apiUrl}/lights`)
  if (res.ok) {
    return res.json()
  }
  throw new Error('Failed to fetch lights')
}

export const getPlugs = async () => {
  const res = await fetch(`${apiUrl}/plugs`)
  if (res.ok) {
    return res.json()
  }
  throw new Error('Failed to fetch plugs')
}

export const getLight = async (id: string) => {
  const res = await fetch(`${apiUrl}/lights/${id}`)
  if (res.ok) {
    return res.json()
  }
  throw new Error('Failed to fetch light')
}

export const getPlug = async (id: string) => {
  const res = await fetch(`${apiUrl}/plugs/${id}`)
  if (res.ok) {
    return res.json()
  }
  throw new Error('Failed to fetch plug')
}

export const setLight = async (id: string, state: LightInput) => {
  const res = await fetch(`${apiUrl}/lights/${id}/state`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(state),
  })
  if (res.ok) {
    return res.json()
  }
  throw new Error('Failed to set light')
}

export const setPlug = async (id: string, state: PlugInput) => {
  const res = await fetch(`${apiUrl}/plugs/${id}/state`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(state),
  })
  if (res.ok) {
    return res.json()
  }
  throw new Error('Failed to set plug')
}

export const connectWebSocket = () => {
  const ws = new WebSocket(`ws://${window.location.host}/ws`)
  ws.addEventListener('open', () => {
    console.log('WebSocket connected')
  })
  ws.addEventListener('close', () => {
    console.log('WebSocket disconnected')
  })
  return ws
}
