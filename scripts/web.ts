import { spawn } from 'child_process'
import fs from 'fs'
import logUpdate from 'log-update'

type Env = 'web'
let env: Env = 'web'

type CommandsObject = {
  [key in Env]: string
}

const previewCommands: CommandsObject = {
  web: 'pnpm preview',
}

const devCommands: CommandsObject = {
  web: 'pnpm dev',
}

const installCommands: CommandsObject = {
  web: 'pnpm install',
}

const buildCommands: CommandsObject = {
  web: 'pnpm build',
}

const checkCommands: CommandsObject = {
  web: 'pnpm check',
}

const preview = () => previewCommands[env] ?? ''

const dev = () => devCommands[env] ?? ''

const install = () => installCommands[env] ?? ''

const build = () => buildCommands[env] ?? ''

const check = () => checkCommands[env] ?? ''

const possibleWebPaths: [string, Env][] = [['HomeApiWeb', 'web']]

type Command = {
  command: () => string
  options: {
    [key: string]: any
  }
}

const commands: {
  [key: string]: Command
} = {
  '--install': { command: install, options: { shell: true, stdio: 'inherit' } },
  '--dev': { command: dev, options: { shell: true, stdio: 'inherit' } },
  '--build': { command: build, options: { shell: true, stdio: 'inherit' } },
  '--preview': { command: preview, options: { shell: true, stdio: 'inherit' } },
  '--check': { command: check, options: { shell: true, stdio: 'inherit' } },
}

function getWebPath() {
  const pathIndex = process.argv.findIndex((arg) => arg === '--path')
  if (pathIndex !== -1) {
    const path = possibleWebPaths.find((webPath) =>
      process.argv[pathIndex + 1].includes(webPath[0])
    )
    if (path) {
      env = path[1]
      return path[0]
    }
    logUpdate('Path does not exist')
    process.exit(1)
  } else {
    const webPath = possibleWebPaths.find((path) => fs.existsSync(path[0]))
    if (!webPath) {
      logUpdate('No web found')
      process.exit(1)
    }
    env = webPath[1]
    return webPath[0]
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
  const path = getWebPath()

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
