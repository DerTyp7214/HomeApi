<script lang="ts">
  import { connectWebSocket, getLights, getPlugs } from '../api'
  import LightElement from '../components/+lightElement.svelte'
  import PlugElement from '../components/+plugElement.svelte'

  let lights: { [key: string]: Light } = {}
  let plugs: { [key: string]: Plug } = {}

  async function loadDevices() {
    const lightsData = await getLights()
    lightsData.forEach((light) => {
      lights[light.id] = light
    })

    const plugsData = await getPlugs()
    plugsData.forEach((plug) => {
      plugs[plug.id] = plug
    })
  }

  const ws = connectWebSocket()

  ws.addEventListener('message', (event) => {
    const { type, data } = JSON.parse(event.data)

    switch (type) {
      case 'light':
        lights[data.id] = data
        break
      case 'plug':
        plugs[data.id] = data
        break
    }
  })

  loadDevices()
</script>

<div class="m-4">
  <button
    class="block p-2 border-2 rounded-lg hover:bg-white/10 transition-all active:bg-white/20"
    on:click={loadDevices}>Reload</button
  >
  <h1 class="text-2xl font-bold mt-5">Lights</h1>
  <div class="inline-flex justify-around mt-3">
    {#each Object.entries(lights) as [_, light]}
      <LightElement {light} />
    {/each}
  </div>

  <h1 class="text-2xl font-bold mt-5">Plugs</h1>
  <div class="inline-flex justify-around mt-3">
    {#each Object.entries(plugs) as [_, plug]}
      <PlugElement {plug} />
    {/each}
  </div>
</div>
