/// <reference types="svelte" />
/// <reference types="vite/client" />

type Light = {
  id: string
  name: string
  on: boolean
  brightness: number
  color: [[number, number, number]]
  reachable: boolean
  type: string
  model: string
  manufacturer: string
  uniqueid: string
  swversion: string
  productid: string
}

type Plug = {
  id: string
  name: string
  on: boolean
  reachable: boolean
  type: string
  model: string
  manufacturer: string
  uniqueid: string
  swversion: string
  productid: string
}

type LightInput = {
  on?: boolean
  brightness?: number
  color?: {
    hue?: number
    saturation?: number
  }
}

type PlugInput = {
  on?: boolean
}
