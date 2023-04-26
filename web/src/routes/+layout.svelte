<script lang="ts">
  import { checkApiUrl, getLights, getPlugs } from '../api'
  import LightElement from '../components/+lightElement.svelte'
  import PlugElement from '../components/+plugElement.svelte'

  let lights: Light[] = []
  let plugs: Plug[] = []

  checkApiUrl().then(async () => {
    lights = await getLights()
    plugs = await getPlugs()
  })
</script>

<div>
  <div class="flex justify-around mt-5">
    {#each lights as light}
      <LightElement {light} />
    {/each}
  </div>

  {#each plugs as plug}
    <PlugElement name={plug.name} />
  {/each}
</div>
