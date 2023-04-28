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