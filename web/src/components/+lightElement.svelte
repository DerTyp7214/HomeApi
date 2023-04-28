<script lang="ts">
  import InfoIcon from 'svelte-material-icons/Information.svelte'

  import { setLight } from '../api'
  import { HSBToRGB, RGBToHEX } from '../utils'
  import Modal, { getModal } from './+modal.svelte'

  export let light: Light

  $: color = RGBToHEX(
    HSBToRGB(light.color.hue, light.color.saturation, light.on ? 0.5 : 0)
  )

  async function toggleLight() {
    light = await setLight(light.id, { on: !light.on })
  }
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<div
  id="light"
  style="--color: {color}"
  class="rounded-md w-36 h-36 flex flex-col justify-center items-center m-2 border-2 cursor-pointer hover:border-4 hover:scale-110 relative"
  on:click={toggleLight}
>
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <div
    class="absolute top-2 right-2 cursor-pointer"
    on:click={(event) => {
      event.preventDefault()
      event.stopPropagation()

      getModal(`modal-${light.name}`).open()
    }}
  >
    <InfoIcon />
  </div>
  <h1 class="text-xl font-bold select-none">{light.name}</h1>
  <h1 class="text-lg font-bold select-none">{light.on ? 'ON' : 'OFF'}</h1>
</div>

<Modal id={`modal-${light.name}`}>
  <h1 slot="header" class="text-xl font-bold select-none">
    {light.name}
  </h1>
  <div class="p-4 flex flex-col justify-center">
    {#each Object.entries(light) as [key, value]}
      {#if Object(value) === value}
        <div class="grid grid-cols-2 mb-5">
          <h1 class="text-lg font-bold select-none">{key}</h1>
          <h1 class="text-lg font-bold select-none">-</h1>
          {#each Object.entries(value) as [key1, value1]}
            <h1 class="text-lg font-bold select-none ml-5">{key1}</h1>
            <h1 class="text-lg font-bold select-none">{value1}</h1>
          {/each}
        </div>
      {:else}
        <div class="grid grid-cols-2">
          <h1 class="text-lg font-bold select-none">{key}</h1>
          <h1 class="text-lg font-bold select-none">{value}</h1>
        </div>
      {/if}
    {/each}
  </div>
</Modal>

<style>
  div#light {
    background: linear-gradient(
      135deg,
      var(--color) 0%,
      color-mix(in xyz, var(--color) 20%, black) 100%
    );

    transition: all 0.2s ease-in-out;
  }
</style>
