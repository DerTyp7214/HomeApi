<script lang="ts">
  import PlusIcon from 'svelte-material-icons/Plus.svelte'

  import {
    connectWebSocket,
    getLights,
    getPlugs,
    hueConfig,
    hueInit,
    hueDelete,
    logout,
  } from '../api'
  import LightElement from '../components/+lightElement.svelte'
  import PlugElement from '../components/+plugElement.svelte'
  import CustomButton from '../components/+customButton.svelte'
  import Modal, { getModal } from '../components/+modal.svelte'

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

    if (!data) {
      loadDevices()
      return
    }

    switch (type) {
      case 'light':
        lights[data.id] = data
        break
      case 'plug':
        plugs[data.id] = data
        break
    }
  })

  async function addHue() {
    getModal('info-modal').close()
    const ip = prompt(
      'Enter the IP of your Hue Bridge, press the button and click OK'
    )
    const config = await hueConfig(ip).catch(() => null)

    if (config) {
      const init = await hueInit(config.id)
        .then(() => true)
        .catch(() => false)

      if (init) {
        loadDevices()
        return
      } else {
        await hueDelete(config.id)
      }
    }
    alert('Something went wrong')
  }

  loadDevices()
</script>

<div class="m-4">
  <div class="flex justify-between">
    <div class="flex space-x-2">
      <CustomButton click={loadDevices}>Reload</CustomButton>
      <CustomButton click={() => getModal('info-modal').open()}>
        <PlusIcon slot="icon" class="me-1" /> Devices
      </CustomButton>
    </div>
    <CustomButton click={logout}>Logout</CustomButton>
  </div>
  <h1 class="text-2xl font-bold mt-5">Lights</h1>
  <div class="inline-flex flex-wrap justify-start mt-3">
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

<Modal id="info-modal">
  <h1 slot="header" class="text-xl font-bold select-none">Add Devices</h1>
  <div class="mt-5 items-start">
    <div class="flex flex-col justify-center items-center">
      <CustomButton click={addHue}>Hue</CustomButton>
    </div>
  </div>
</Modal>
