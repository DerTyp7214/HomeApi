import { spawn } from 'child_process'
import fs from 'fs'
import logUpdate from 'log-update'

type Env = 'python' | 'rust'
let env: Env = 'python'

type CommandsObject = {
  [key in Env]: string
}

const startCommands: CommandsObject = {
  python: 'python main.py',
  rust: 'cargo run --release',
}

const devCommands: CommandsObject = {
  python: 'uvicorn app:app --reload --host 0.0.0.0',
  rust: 'cargo run',
}

const installCommands: CommandsObject = {
  python: 'pip3 install -r requirements.txt',
  rust: 'echo "No install command"',
}

const buildCommands: CommandsObject = {
  python: 'echo "No build command"',
  rust: 'cargo build --release',
}

const start = () => startCommands[env] ?? ''

const dev = () => devCommands[env] ?? ''

const install = () => installCommands[env] ?? ''

const build = () => buildCommands[env] ?? ''

const possibleApiPaths: [string, Env][] = [
  ['HomeApiPython', 'python'],
  ['HomeApiRust', 'rust'],
]

type Command = {
  command: () => string
  options: {
    [key: string]: any
  }
}

const commands: {
  [key: string]: Command
} = {
  '--start': { command: start, options: { shell: true, stdio: 'inherit' } },
  '--dev': { command: dev, options: { shell: true, stdio: 'inherit' } },
  '--install': { command: install, options: { shell: true } },
  '--build': { command: build, options: { shell: true, stdio: 'inherit' } },
}

function getApiPath() {
  const pathIndex = process.argv.findIndex((arg) => arg === '--path')
  if (pathIndex !== -1) {
    const path = possibleApiPaths.find((apiPath) =>
      process.argv[pathIndex + 1].includes(apiPath[0])
    )
    if (path) {
      env = path[1]
      return path[0]
    }
    logUpdate('Path does not exist')
    process.exit(1)
  } else {
    const apiPath = possibleApiPaths.find((path) => fs.existsSync(path[0]))
    if (!apiPath) {
      logUpdate('No api found')
      process.exit(1)
    }
    env = apiPath[1]
    return apiPath[0]
  }
}

function getCommand(): Command {
  const command = process.argv[2] as keyof typeof commands

  if (commands[command]) return commands[command]

  logUpdate('No command found')
  process.exit(1)
}

async function main() {
  const { command, options } = getCommand()
  const path = getApiPath()

  const commandOptions: any = Object.assign(
    {
      cwd: path,
      shell: true,
    },
    options
  )

  const child = spawn(command(), commandOptions)

  if (commandOptions.stdio !== 'inherit') {
    logUpdate.done()
    child.stdout.on('data', (data) => {
      logUpdate(data.toString())
    })
  }

  child.on('exit', (code: number) => {
    logUpdate(`Exited with code ${code}`)
    process.exit(code)
  })
}

main()
