export const HSBToRGB = (h, s, b) => {
  s /= 100
  const k = (n) => (n + h / 60) % 6
  const f = (n) => b * (1 - s * Math.max(0, Math.min(k(n), 4 - k(n), 1)))
  return [
    Math.round(255 * f(5)),
    Math.round(255 * f(3)),
    Math.round(255 * f(1)),
  ]
}

export const RGBToHEX = ([r, g, b]: number[]) => {
  return '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)
}