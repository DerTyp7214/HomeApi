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

# check if python3 is installed and install if not
$ErrorActionPreference = 'SilentlyContinue'
python3 -V > $null 2>&1
$ErrorActionPreference = 'Continue'

if ($?) {
  Write-Host "python3 already installed"
} else {
  Write-Host "Installing python3"
  winget install -e --id Python.Python.3.11
}

pnpm install
pnpm install:api
pnpm install:web