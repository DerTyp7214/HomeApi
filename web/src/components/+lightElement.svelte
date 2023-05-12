<script lang="ts">
  import { Dropdown, DropdownItem, MenuButton } from 'flowbite-svelte'
  import Color from 'color'

  import { setLight } from '../api'
  import { changeLightnessOfRgb } from '../utils'
  import Modal, { getModal } from './+modal.svelte'

  export let light: Light

  $: color = light.on ? changeLightnessOfRgb(light.color[0], 0.35) : '#000000'

  async function toggleLight() {
    light = await setLight(light.id, { on: !light.on })
  }

  async function changeColor(event: MouseEvent) {
    event.stopPropagation()

    dropdownOpen = false

    const input = document.getElementById(
      `color-input-${light.id}`
    ) as HTMLInputElement
    input.value = Color.rgb(light.color[0]).hex()
    input.onchange = async () => {
      const color = Color(input.value)
      light = await setLight(light.id, {
        color: [[color.red(), color.green(), color.blue()]],
      })
    }
    input.onclick = (event) => event.stopPropagation()
    input.click()
  }

  let dropdownOpen = false
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<div
  id="light"
  style="--color: {color}"
  class="rounded-md w-36 h-36 flex flex-col justify-center items-center m-2 border-2 cursor-pointer hover:border-4 hover:scale-110 relative"
  on:click={toggleLight}
>
  <MenuButton
    class="dots-menu-{light.id} absolute top-2 right-2 dark:text-white"
    on:click={(e) => e.stopPropagation()}
    vertical
  />
  <h1 class="text-xl font-bold select-none">{light.name}</h1>
  <h1 class="text-lg font-bold select-none">{light.on ? 'ON' : 'OFF'}</h1>

  <input type="color" class="w-0 h-0 opacity-0" id="color-input-{light.id}" />
</div>

<Dropdown triggeredBy=".dots-menu-{light.id}" bind:open={dropdownOpen}>
  <DropdownItem on:click={changeColor}>Change Color</DropdownItem>
  <DropdownItem
    slot="footer"
    on:click={(event) => {
      event.stopPropagation()
      getModal(`modal-${light.name}`).open()
    }}>Info</DropdownItem
  >
</Dropdown>

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
