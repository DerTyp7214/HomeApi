import chalk from 'chalk'
import { exec } from 'child_process'
import fs from 'fs-extra'
import logUpdate from 'log-update'
import { createInterface } from 'readline/promises'

const run = async () => {
  const { stdout, stderr } = await exec('pnpm build:web')

  logUpdate(chalk.green('Building web...'))
  logUpdate.done()

  stdout?.pipe(process.stdout)
  stderr?.pipe(process.stderr)

  await new Promise((resolve) => {
    stdout?.on('end', resolve)
    stderr?.on('end', resolve)
  })

  logUpdate()
  logUpdate.done()
  logUpdate(chalk.green('Moving web to server...'))

  fs.removeSync('api/dist')
  fs.moveSync('web/dist', 'api/dist')

  logUpdate()
  logUpdate.done()
  logUpdate()

  const readline = createInterface({
    input: process.stdin,
    output: process.stdout,
  })

  const answer = await readline.question(
    chalk.yellow('Do you want to start the server? (y/n) ')
  )

  if (answer.toLowerCase() !== 'y') {
    process.exit(0)
  }

  const {
    stdout: fastApiOut,
    stderr: fastApiError,
    pid,
  } = await exec('pnpm start:api')

  const kill = () => {
    if (pid) process.kill(pid)
    process.exit(0)
  }

  process.on('SIGINT', kill)
  process.on('SIGUSR1', kill)
  process.on('SIGUSR2', kill)

  logUpdate(chalk.green('Starting server...'))

  fastApiOut?.pipe(process.stdout)
  fastApiError?.pipe(process.stderr)

  await new Promise((resolve) => {
    fastApiOut?.on('end', resolve)
    fastApiError?.on('end', resolve)
  })

  logUpdate()
  logUpdate.done()

  logUpdate(chalk.red('Server stopped.'))
  process.exit(0)
}

run()
