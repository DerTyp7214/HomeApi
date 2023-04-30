#!/bin/bash -i

function printGreen() {
    printf "\e[32m$1\e[0m\n"
}

function printRed() {
    printf "\e[31m$1\e[0m\n"
}

function printYellow() {
    printf "\e[33m$1\e[0m\n"
}

if ! [ -x "$(command -v docker)" ]; then
  printRed 'Error: docker is not installed.' >&2
  printYellow 'Installing docker...'
  
  sudo apt-get update
  sudo apt-get install -y docker.io
  sudo systemctl start docker
  sudo systemctl enable docker
  
  printGreen 'Docker installed.'
else
  printGreen 'Docker is installed.'
fi