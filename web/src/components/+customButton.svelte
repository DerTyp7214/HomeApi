<script lang="ts">
  export let type: 'button' | 'submit' | 'reset' = 'button'
  export let click: () => void = () => {}
</script>

<button
  {type}
  class="flex flex-row items-center justify-center p-2 border-2 rounded-lg hover:bg-white/10 transition-all active:bg-white/20"
  on:click={click}
>
  <slot name="icon" />
  <span>
    <slot />
  </span>
</button>
