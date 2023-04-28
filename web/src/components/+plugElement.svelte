<script lang="ts">
  import InfoIcon from 'svelte-material-icons/Information.svelte'

  import { setPlug } from '../api'
  import Modal, { getModal } from './+modal.svelte'

  export let plug: Plug

  async function togglePlug() {
    plug = await setPlug(plug.id, { on: !plug.on })
  }

  $: color = plug.on ? 'green' : 'red'
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<div
  id="plug"
  style="--color: {color}"
  class="rounded-md w-36 h-36 flex flex-col justify-center items-center m-2 border-2 cursor-pointer hover:border-4 hover:scale-110 relative"
  on:click={togglePlug}
>
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <div
    class="absolute top-2 right-2 cursor-pointer"
    on:click={(event) => {
      event.preventDefault()
      event.stopPropagation()

      getModal(`modal-${plug.name}`).open()
    }}
  >
    <InfoIcon />
  </div>
  <h1 class="text-xl font-bold select-none">{plug.name}</h1>
  <h1 class="text-lg font-bold select-none">{plug.on ? 'ON' : 'OFF'}</h1>
</div>

<Modal id={`modal-${plug.name}`}>
  <h1 slot="header" class="text-xl font-bold select-none">
    {plug.name}
  </h1>
  <div class="p-4 flex flex-col justify-center">
    {#each Object.entries(plug) as [key, value]}
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
  div#plug {
    background: linear-gradient(
      135deg,
      var(--color) 0%,
      color-mix(in xyz, var(--color) 20%, black) 100%
    );

    transition: all 0.2s ease-in-out;
  }
</style>
