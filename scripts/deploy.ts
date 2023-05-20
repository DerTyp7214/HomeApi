import chalk from 'chalk'
import { exec } from 'child_process'
import fs from 'fs-extra'
import logUpdate from 'log-update'
import { join } from 'path'

const run = async () => {
  const { stdout, stderr } = exec('pnpm build:web')

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

  const possibleApiPaths: string[] = [
    join('HomeApiPython', 'app'),
    'HomeApiRust',
  ]

  const pathIndex = process.argv.findIndex((arg) => arg === '--path')

  let path = possibleApiPaths.find((path) => fs.existsSync(path))

  if (pathIndex !== -1) {
    let tmpPath = possibleApiPaths.find((apiPath) =>
      process.argv[pathIndex + 1].includes(apiPath)
    )
    path = tmpPath ? tmpPath : path
  }

  const distPath = join(path!, 'dist')

  fs.removeSync(distPath)
  fs.moveSync('web/dist', distPath)

  logUpdate(chalk.green('Done!'))
  logUpdate.done()
}

run()
