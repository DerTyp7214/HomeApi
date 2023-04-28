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
Write-Host "This script will install node, pnpm, mongodb, python3, and winget." -f Yellow
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

$ErrorActionPreference = 'SilentlyContinue'
Get-ChildItem "C:\Program Files\MongoDB" > $null 2>&1

if ($?) {
  Write-Host "MongoDB already installed" -f Green
} else {
  Write-Host "Installing mongodb" -f Yellow
  winget install -e --id MongoDB.Server
  Write-Host "Installing mongodb compass" -f Yellow
  winget install -e --id MongoDB.Compass.Community

  Write-Host "MongoDB and MongoDB Compass installed" -f Green
}

$ErrorActionPreference = 'SilentlyContinue'
mongosh --version > $null 2>&1

if ($?) {
  Write-Host "mongosh already downloaded and in path" -f Green
} else {
  $ErrorActionPreference = 'SilentlyContinue'
  Get-ChildItem ".\mongodb\bin\mongosh.exe" > $null 2>&1
  $ErrorActionPreference = 'Continue'

  if ($?) {
    Write-Host "mongosh already downloaded" -f Green
    Write-Host "Adding mongosh to path" -f Yellow
    $env:Path += ";$pwd\mongodb\bin"
    Write-Host "mongosh added to path" -f Green
  } else {
    Write-Host "Downloading mongodb shell" -f Yellow
    
    mkdir .\mongodb
    Invoke-WebRequest https://downloads.mongodb.com/compass/mongosh-1.8.2-win32-x64.zip -OutFile .\mongodb\mongosh.zip
    Expand-Archive -Path .\mongodb\mongosh.zip -DestinationPath .\mongodb\bin
    Rename-Item .\mongodb\bin -NewName "bin_old"
    Move-Item .\mongodb\bin_old\mongosh-1.8.2-win32-x64\* .\mongodb\
    Remove-Item .\mongodb\bin_old\mongosh-1.8.2-win32-x64 -Recurse
    Remove-Item .\mongodb\mongosh.zip

    $env:Path += ";$pwd\mongodb\bin"

    Write-Host "MongoDB shell downloaded and added to path" -f Green
  }
}

$ErrorActionPreference = 'SilentlyContinue'
Get-Service -Name "MongoDB" > $null 2>&1

if ($?) {
  Write-Host "MongoDB already running" -f Green
} else {
  Write-Host "Starting MongoDB" -f Yellow
  Start-Service MongoDB

  Write-Host "MongoDB started" -f Green
}

# check if database and collections exist and create if not
$ErrorActionPreference = 'SilentlyContinue'
mongosh --eval "db.getMongo()" > $null 2>&1

if ($?) {
  Write-Host "Mongo is Running" -f Green

  $ErrorActionPreference = 'SilentlyContinue'
  $output = mongosh --eval "db.getMongo().getDBNames().indexOf('web')"
  $ErrorActionPreference = 'Continue'

  if ($output -like "*-1") {
    Write-Host "Database web does not exist" -f Yellow
    Write-Host "Creating database web" -f Yellow
    mongosh web --eval "db.createCollection('config')"
    Write-Host "Database web created" -f Green
  } else {
    Write-Host "Database web already exists" -f Green
    Write-Host "Checking if collections exist" -f Yellow

    $ErrorActionPreference = 'SilentlyContinue'
    $output = mongosh web --eval "db.getCollectionNames().indexOf('config')"
    $ErrorActionPreference = 'Continue'

    if ($output -like "*-1") {
      Write-Host "Collection config does not exist" -f Yellow
      Write-Host "Creating collection config" -f Yellow
      mongosh web --eval "db.createCollection('config')"
      Write-Host "Collection config created" -f Green
    } else {
      Write-Host "Collection config already exists" -f Green
    }
  }
} else {
  Write-Host "Mongo is not Running" -f Red
  exit
}


Write-Host "Installing dependencies" -f Yellow

pnpm install
pnpm install:api
pnpm install:web