$ErrorActionPreference = 'SilentlyContinue'

Write-Host "This script will docker and build the docker image." -f Yellow
Read-Host "Do you wish to continue?" -f Yellow -NoNewline

if ($confirmation -eq "y") {
    Write-Host "Continuing with setup" -f Green
} else {
    Write-Host "Exiting setup" -f Red
    exit
}

if (Get-Package -Name "Docker Desktop") {
    Write-Host "Docker is installed and running." -f Green
} else {
    Write-Host "Docker is not installed or not running." -f Red

    Write-Host "Installing Docker" -f Yellow

    winget install -e --id Docker.DockerDesktop

    Write-Host "Docker installed" -f Green
}