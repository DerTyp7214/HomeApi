<script lang="ts">
  import { setPlug } from '../api'

  export let plug: Plug

  async function togglePlug() {
    plug = await setPlug(plug.id, { on: !plug.on })
  }

  $: color = plug.on ? 'green' : 'red'
</script>

<div
  style="--color: {color}"
  class="rounded-md w-36 h-36 flex flex-col justify-center items-center m-2 border-2 cursor-pointer hover:border-4 hover:scale-110"
  on:click={togglePlug}
  on:keyup={() => {}}
>
  <h1 class="text-xl font-bold select-none">{plug.name}</h1>
  <h1 class="text-lg font-bold select-none">{plug.on ? 'ON' : 'OFF'}</h1>
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
