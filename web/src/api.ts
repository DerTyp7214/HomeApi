let _apiUrl =
  localStorage.getItem('apiUrl') ??
  `${window.location.protocol}//${window.location.host}/api`

export const apiUrl = _apiUrl

export const setApiUrl = (url: string) => {
  _apiUrl = url
  localStorage.setItem('apiUrl', url)
  return localStorage.getItem('apiUrl')
}

export const checkApiUrl = async (count: number = 0) => {
  if (count > 3) {
    return false
  }
  try {
    const res = await fetch(`${apiUrl}/status`).then((res) => res.json())
    if (res.status === 'OK') {
      return true
    }
  } catch (e) {
    console.error(e)
  }
  console.log(_apiUrl, localStorage.getItem('apiUrl'))
  setApiUrl(prompt('API URL', _apiUrl))
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

export const hueConfig = async (ip: string) => {
  const res = await fetch(`${apiUrl}/hue/config`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ host: ip }),
  })
  if (res.ok) {
    return true
  }
  throw new Error('Failed to set config')
}

export const hueInit = async () => {
  const res = await fetch(`${apiUrl}/hue/init`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  })
  if (res.ok) {
    return res.json()
  }
  throw new Error('Failed to init hue')
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
