$ErrorActionPreference = 'SilentlyContinue'
pnpm -v > $null 2>&1
$ErrorActionPreference = 'Continue'

if ($?) {
  Write-Host "pnpm already installed"
} else {
  Write-Host "Installing pnpm"
  Invoke-WebRequest https://get.pnpm.io/install.ps1 -useb | iex
}

$ErrorActionPreference = 'SilentlyContinue'
node -v > $null 2>&1
$ErrorActionPreference = 'Continue'
if ($?) {
  Write-Host "nodejs already installed"
} else {
  Write-Host "Installing nodejs"
  winget install -e --id OpenJS.Nodejs
}

pnpm install
pnpm install:api
pnpm install:web