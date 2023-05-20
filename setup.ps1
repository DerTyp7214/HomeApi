$esc = "$([char]27)"
$WrapBorder = "$esc[36m{0}$esc[0m"

function MakeTop {
  $string = "┌─"
  for($i = 0; $i -lt $Host.UI.RawUI.BufferSize.Width - 4; $i++)
  {
      $string = $string + "─"
  }
  $string = $string + "─┐"

  return $WrapBorder -f $string
}

function MakeBottom {
  $string = "└─"
  for($i = 0; $i -lt $Host.UI.RawUI.BufferSize.Width - 4; $i++)
  {
      $string = $string + "─"
  }
  $string = $string + "─┘"

  return $WrapBorder -f $string
}

function MakeSpaces {
    $string = "│ "
    for($i = 0; $i -lt $Host.UI.RawUI.BufferSize.Width - 4; $i++)
    {
        $string = $string + " "
    }
    $string = $string + " │"
    return $WrapBorder -f $string
}

function CenterText {
    param($Message, $Ansi = "97", $Bold = $false)

    if ($Bold) { $Ansi = "1;${Ansi}" }

    $WrapFormat = "$esc[${Ansi}m{0}$esc[0m"

    $string = $WrapBorder -f "│ "

    for($i = 0; $i -lt (([Math]::Max(0, $Host.UI.RawUI.BufferSize.Width / 2) - [Math]::Max(0, $Message.Length / 2))) - 3; $i++)
    {
        $string = $string + " "
    }

    $string = $string + $WrapFormat -f $Message

    for($i = 0; $i -lt ($Host.UI.RawUI.BufferSize.Width - ((([Math]::Max(0, $Host.UI.RawUI.BufferSize.Width / 2) - [Math]::Max(0, $Message.Length / 2))) - 2 + $Message.Length)) - 3; $i++)
    {
        $string = $string + " "
    }

    $string = $string + $WrapBorder -f " │"
    return $string
}

$MakeTop = MakeTop
$MakeBottom = MakeBottom
$MakeSpaces = MakeSpaces

$HomeApi = CenterText "Home Api" "92" $true
$Welcome = CenterText "Welcome to the setup script for the project" "95"

clear

$MakeTop
$MakeSpaces
$MakeSpaces
$MakeSpaces

Write-Host $HomeApi

$MakeSpaces

Write-Host $Welcome

$MakeSpaces
$MakeSpaces
$MakeSpaces
$MakeBottom

Write-Host
Write-Host "This script will install node, pnpm, python3, and winget." -f Yellow
Write-Host "Do you wish to continue?" -f Yellow -NoNewline
Write-Host " (y/n): " -f White -NoNewline
$confirmation = Read-Host

if ($confirmation -eq "y") {
  Write-Host "Continuing with setup" -f Green
} else {
  Write-Host "Exiting setup" -f Red
  exit
}


$ErrorActionPreference = 'SilentlyContinue'
pnpm -v > $null 2>&1

if ($?) {
  Write-Host "pnpm already installed" -f Green
} else {
  Write-Host "Installing pnpm" -f Yellow
  Invoke-WebRequest https://get.pnpm.io/install.ps1 -useb | iex

  Write-Host "pnpm installed" -f Green
}

$ErrorActionPreference = 'SilentlyContinue'
winget -v > $null 2>&1

if ($?) {
  Write-Host "winget already installed" -f Green
} else {
  Write-Host "winget not installed, please install winget (https://github.com/microsoft/winget-cli)" -f Red
}

$ErrorActionPreference = 'SilentlyContinue'
node -v > $null 2>&1

if ($?) {
  Write-Host "nodejs already installed" -f Green
} else {
  Write-Host "Installing nodejs" -f Yellow
  winget install -e --id OpenJS.Nodejs

  Write-Host "Nodejs installed" -f Green
}

# check if python3 is installed and install if not
$ErrorActionPreference = 'SilentlyContinue'
python3 -V > $null 2>&1

if ($?) {
  Write-Host "python3 already installed" -f Green
} else {
  Write-Host "Installing python3" -f Yellow
  winget install -e --id Python.Python.3.11

  Write-Host "Python3 installed" -f Green
}

Write-Host "Installing dependencies" -f Yellow

pnpm run setup

pnpm install
pnpm install:api
pnpm install:web

Write-Host "Dependencies are installed" -f Green
Write-Host "Generating api-key secret" -f Yellow

$SECRET = python3 -c "import os; import binascii; print(binascii.hexlify(os.urandom(32)))"
$ALGORITHM = "HS256"

$prefix = "b'"
$suffix = "'"
$startIndex = $SECRET.IndexOf($prefix) + $prefix.Length
$endIndex = $SECRET.IndexOf($suffix, $startIndex)
$substring = $SECRET.Substring($startIndex, $endIndex - $startIndex)

if (Test-Path "HomeApiPython") {
  "secret=$substring" | Out-File -FilePath "HomeApiPython\.env" -Encoding ascii
  "algorithm=$ALGORITHM" | Out-File -FilePath "HomeApiPython\.env" -Encoding ascii -Append
} else if (Test-Path "HomeApiRust") {
  "secret=$substring" | Out-File -FilePath "HomeApiRust\.env" -Encoding ascii
  "algorithm=$ALGORITHM" | Out-File -FilePath "HomeApiRust\.env" -Encoding ascii -Append
} else {
  Write-Host "HomeApiPython or HomeApiRust not found" -f Red
  exit
}

Write-Host "api-key secret is generated" -f Green
Write-Host "Setup is complete\n" -f Green
Write-Host "Run 'pnpm deploy:web' to deploy the web server" -f Green
Write-Host "Run 'pnpm start:api' to start the api server" -f Green

Write-Host "Do you want to deploy the web server and start the api server?" -f Yellow -NoNewline
Write-Host " (y/n): " -NoNewline -f White
$answer = Read-Host

if ($answer -like "y") {
  Write-Host "Deploying web server" -f Yellow
  pnpm deploy:web
  Write-Host "Web server deployed" -f Green
  Write-Host "Starting api server" -f Yellow
  pnpm start:api
  Write-Host "Api server started" -f Green
}