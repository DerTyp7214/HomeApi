<script lang="ts">
  import { checkApiUrl } from './api'
  import Layout from './routes/+layout.svelte'

  let connected = false
  let error = false

  checkApiUrl()
    .then(() => {
      connected = true
    })
    .catch(() => {
      error = true
    })
</script>

<main>
  {#if connected}
    <Layout />
  {:else if error}
    <h1 class="text-2xl font-bold">Error</h1>
  {:else}
    <h1 class="text-2xl font-bold">Loading...</h1>
  {/if}
</main>

<style global>
  @tailwind base;
  @tailwind components;
  @tailwind utilities;
</style>
