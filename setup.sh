#!/bin/bash

terminalWidth=$(tput cols)

function centerText() {
    textLength=${#1}
    spaces=$((terminalWidth-textLength-2))
    leftSpaces=$((spaces/2))
    rightSpaces=$((spaces-leftSpaces+2))

    printf "\e[36m│\e[0m"
    for ((i=1; i < $leftSpaces; i++)); do
        printf " "
    done
    if [ "$3" = true ]; then
        printf "\e[1;${2}m$1\e[0m"
    else
        printf "\e[${2}m$1\e[0m"
    fi
    for ((i=1; i < $rightSpaces; i++)); do
        printf " "
    done
    printf "\e[36m│\e[0m\n"
}

function spaces() {
    printf "\e[36m│\e[0m" 
    for ((j=1; j < $terminalWidth - 1; j++)); do
        printf " "
    done
    printf "\e[36m│\e[0m\n"
}

function topBorder() {
    printf "\e[36m┌"
    for ((i=1; i < $terminalWidth - 1; i++)); do
        printf "─"
    done
    printf "┐\e[0m\n"
}

function bottomBorder() {
    printf "\e[36m└"
    for ((i=1; i < $terminalWidth - 1; i++)); do
        printf "─"
    done
    printf "┘\e[0m\n"
}

clear

topBorder
spaces
spaces
spaces
centerText "Home Api" "32" true
spaces
centerText "Welcome to the setup script for the project" "95"
spaces
spaces
spaces
bottomBorder

printf "\n\e[33mThis script will install node, npm, pnpm, python3, and pip3.\nDo you wish to continue?\e[0m" -n
read -p " (y/n): " yn

case $yn in
    [Yy]* ) ;;
    [Nn]* ) exit;;
    * ) echo "Please answer yes or no.";;
esac

if which node >/dev/null ; then
    echo "node is already installed."
else
    echo "Installing node."

    if [ -x "$(command -v apt-get)" ]; then
    sudo apt-get update

    sudo apt-get install -y nodejs

    elif [ -x "$(command -v pacman)" ]; then
        sudo pacman -S nodejs

    elif [ -x "$(command -v pkg)" ]; then
        sudo pkg install node

    elif [ -x "$(command -v brew)" ]; then
        sudo brew install node

    else
        echo "Unable to determine package manager for this system"
        exit 1
    fi

    if [ -x "$(command -v node)" ] && [ -x "$(command -v npm)" ]; then
        echo "Node.js and npm were installed successfully"
    else
        echo "Node.js and/or npm were not installed successfully"
    fi
fi


if which pnpm >/dev/null ; then
    echo "pnpm is already installed."
else
    echo "Installing pnpm."

    if which curl >/dev/null ; then
        echo "Downloading via curl."
        curl -fsSL https://get.pnpm.io/install.sh | sh -
    elif which wget >/dev/null ; then
        echo "Downloading via wget."
        wget -qO- https://get.pnpm.io/install.sh | sh -
    else
        echo "Cannot download, neither wget nor curl is available."
        exit 1
    fi

    source ~/.bashrc
    echo "pnpm is installed."
fi

if which python3 >/dev/null ; then
    echo "python3 is already installed."
else
    echo "Installing python3."

    if which curl >/dev/null ; then
        echo "Downloading via curl."
        curl -fsSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -
    elif which wget >/dev/null ; then
        echo "Downloading via wget."
        wget -qO- https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -
    else
        echo "Cannot download, neither wget nor curl is available."
        exit 1
    fi

    echo "python3 is installed."
fi

if which pip3 >/dev/null ; then
    echo "pip3 is already installed."
elif which ~/.local/bin/pip3 >/dev/null ; then
    echo "pip3 is already installed."
    echo "adding ~/.local/bin to PATH"

    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        if cat ~/.bashrc | grep "# LOCAL_BIN_PATH" > /dev/null ; then
            echo "LOCAL_BIN_PATH is already in .bashrc"
            source ~/.bashrc
        else
            echo "adding LOCAL_BIN_PATH to .bashrc"
            echo "" >> ~/.bashrc
            echo "# LOCAL_BIN_PATH" >> ~/.bashrc
            echo "export PATH=$PATH:$HOME/.local/bin" >> ~/.bashrc
            source ~/.bashrc
        fi
    fi
else
    echo "Installing pip3."

    if which curl >/dev/null ; then
        echo "Downloading via curl."
        curl -fsSL https://bootstrap.pypa.io/get-pip.py | python3 -
    elif which wget >/dev/null ; then
        echo "Downloading via wget."
        wget -qO- https://bootstrap.pypa.io/get-pip.py | python3 -
    else
        echo "Cannot download, neither wget nor curl is available."
        exit 1
    fi

    echo "pip3 is installed."
fi


pnpm install
pnpm install:api
pnpm install:web