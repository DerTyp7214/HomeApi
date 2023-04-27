Write-Host "This script will install node, pnpm, python3, and winget. Please confirm that you want to continue (y/n)"
$confirmation = Read-Host

if ($confirmation -eq "y") {
  Write-Host "Continuing with setup"
} else {
  Write-Host "Exiting setup"
  exit
}


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
winget -v > $null 2>&1
$ErrorActionPreference = 'Continue'

if ($?) {
  Write-Host "winget already installed"
} else {
  Write-Host "winget not installed, please install winget (https://github.com/microsoft/winget-cli)"
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