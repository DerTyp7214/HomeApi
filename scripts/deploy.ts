import chalk from 'chalk'
import { exec } from 'child_process'
import fs from 'fs-extra'
import logUpdate from 'log-update'

const run = async () => {
  const { stdout, stderr } = await exec('pnpm build:web')

  logUpdate(chalk.yellow('Building web...'))
  logUpdate.done()

  stdout?.pipe(process.stdout)
  stderr?.pipe(process.stderr)

  await new Promise((resolve) => {
    stdout?.on('end', resolve)
    stderr?.on('end', resolve)
  })

  logUpdate(chalk.green('Done!'))
  logUpdate()
  logUpdate.done()
  logUpdate(chalk.yellow('Moving web to server...'))

  fs.removeSync('api/dist')
  fs.moveSync('web/dist', 'api/dist')

  logUpdate(chalk.green('Done!'))
  logUpdate.done()
}

run()
