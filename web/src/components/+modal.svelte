<script lang="ts" context="module">
  const modals = {}

  export function getModal(id = '') {
    return modals[id]
  }
</script>

<script>
  import CloseIcon from 'svelte-material-icons/Close.svelte'

  export let id = ''

  let dialog

  $: if (dialog) {
    modals[id] = {
      close: () => dialog.close(),
      open: () => dialog.showModal(),
    }
  }
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<dialog
  bind:this={dialog}
  on:click|self={() => dialog.close()}
>
  <div on:click|stopPropagation class="relative">
    <button
      class="absolute top-2 right-2 cursor-pointer hover:bg-gray-200/20 active:bg-gray-200/30 rounded-full p-1 transition-colors focus:outline-none"
      on:click={() => dialog.close()}
    >
      <CloseIcon />
    </button>
    <slot name="header" />
    <hr />
    <slot />
  </div>
</dialog>

<style>
  dialog {
    border-radius: 0.8em;
    border: none;
    padding: 0;
  }
  dialog::backdrop {
    background: rgba(0, 0, 0, 0.3);
  }
  dialog > div {
    padding: 1em;
  }
  dialog[open] {
    animation: zoom 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  }
  @keyframes zoom {
    from {
      transform: scale(0.95);
    }
    to {
      transform: scale(1);
    }
  }
  dialog[open]::backdrop {
    animation: fade 0.2s ease-out;
  }
  @keyframes fade {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }
  button {
    display: block;
  }
</style>
