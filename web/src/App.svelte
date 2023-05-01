<script lang="ts">
  import { checkApiUrl, checkApiKey, login, signup } from './api'
  import Layout from './routes/+layout.svelte'

  let connected = false
  let error = false

  let authorized = false
  let unauthorized = false

  let doSignup = false

  checkApiUrl()
    .then(() => {
      connected = true
    })
    .catch(() => {
      error = true
    })

  checkApiKey()
    .then(() => {
      unauthorized = false
      authorized = true
    })
    .catch(() => {
      authorized = false
      unauthorized = true
    })

  function submitLogin(event: SubmitEvent) {
    const form = event.target as HTMLFormElement
    const email = form.email.value
    const password = form.password.value

    login(email, password)
      .then(() => {
        unauthorized = false
        authorized = true
      })
      .catch(() => {
        authorized = false
        unauthorized = true
      })
  }

  function submitSignup(event: SubmitEvent) {
    const form = event.target as HTMLFormElement
    const username = form.username.value
    const email = form.email.value
    const password = form.password.value

    signup(username, email, password)
      .then(() => {
        authorized = true
        unauthorized = false
      })
      .catch(() => {
        authorized = false
        unauthorized = true
      })
  }
</script>

<main>
  {#if unauthorized}
    {#if doSignup}
      <form
        autocomplete="off"
        class="flex flex-col items-center justify-center w-full h-screen"
        on:submit|preventDefault={submitSignup}
      >
        <h1 class="text-2xl font-bold">Signup</h1>
        <input
          class="transition-all w-10/12 lg:w-1/2 2xl:w-1/3 p-2 m-2 border border-gray-400 rounded"
          type="text"
          name="username"
          placeholder="Username"
        />
        <input
          class="transition-all w-10/12 lg:w-1/2 2xl:w-1/3 p-2 m-2 border border-gray-400 rounded"
          type="email"
          name="email"
          placeholder="Email"
        />
        <input
          class="transition-all w-10/12 lg:w-1/2 2xl:w-1/3 p-2 m-2 border border-gray-400 rounded"
          type="password"
          name="password"
          placeholder="Password"
        />
        <button
          class="transition-all w-10/12 lg:w-1/2 2xl:w-1/3 p-2 m-2 text-white bg-blue-500 rounded hover:bg-blue-700"
          type="submit"
        >
          Signup
        </button>
        <p class="text-sm">
          Already have an account?{' '}
          <!-- svelte-ignore a11y-click-events-have-key-events -->
          <span
            class="text-blue-500 hover:text-blue-700 cursor-pointer"
            on:click={() => (doSignup = false)}
          >
            Login
          </span>
        </p>
      </form>
    {:else}
      <form
        autocomplete="off"
        class="flex flex-col items-center justify-center w-full h-screen"
        on:submit|preventDefault={submitLogin}
      >
        <h1 class="text-2xl font-bold">Login</h1>
        <input
          class="transition-all w-10/12 lg:w-1/2 2xl:w-1/3 p-2 m-2 border border-gray-400 rounded"
          type="email"
          name="email"
          placeholder="Email"
        />
        <input
          class="transition-all w-10/12 lg:w-1/2 2xl:w-1/3 p-2 m-2 border border-gray-400 rounded"
          type="password"
          name="password"
          placeholder="Password"
        />
        <button
          class="transition-all w-10/12 lg:w-1/2 2xl:w-1/3 p-2 m-2 text-white bg-blue-500 rounded hover:bg-blue-700"
          type="submit"
        >
          Login
        </button>
        <p class="text-sm">
          Don't have an account?{' '}
          <!-- svelte-ignore a11y-click-events-have-key-events -->
          <span
            class="text-blue-500 hover:text-blue-700 cursor-pointer"
            on:click={() => (doSignup = true)}
          >
            Signup
          </span>
        </p>
      </form>
    {/if}
  {:else if authorized}
    {#if connected}
      <Layout />
    {:else if error}
      <h1 class="text-2xl font-bold">Error</h1>
    {:else}
      <h1 class="text-2xl font-bold">Loading...</h1>
    {/if}
  {:else}
    <h1 class="text-2xl font-bold">Something went wrong!</h1>
  {/if}
</main>

<style global>
  @tailwind base;
  @tailwind components;
  @tailwind utilities;
</style>
