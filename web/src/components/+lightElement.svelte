<script lang="ts">
  import { setLight } from '../api'
  import { HSBToRGB, RGBToHEX } from '../utils'

  export let light: Light

  $: color = RGBToHEX(
    HSBToRGB(light.color.hue, light.color.saturation, light.on ? 0.5 : 0)
  )

  async function toggleLight() {
    light = await setLight(light.id, { on: !light.on })
  }
</script>

<div
  style="--color: {color}"
  class="rounded-md w-36 h-36 flex flex-col justify-center items-center m-2 border-2 cursor-pointer hover:border-4 hover:scale-110"
  on:click={toggleLight}
>
  <h1 class="text-xl font-bold select-none">{light.name}</h1>
  <h1 class="text-lg font-bold select-none">{light.on ? 'ON' : 'OFF'}</h1>
</div>

<style>
  div {
    background: linear-gradient(
      135deg,
      var(--color) 0%,
      color-mix(in xyz, var(--color) 20%, black) 100%
    );

    transition: all 0.2s ease-in-out;
  }
</style>
