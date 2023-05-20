#!/bin/bash -i

terminalWidth=$(tput cols)

function printGreen() {
    printf "\e[32m$1\e[0m\n"
}

function printRed() {
    printf "\e[31m$1\e[0m\n"
}

function printYellow() {
    printf "\e[33m$1\e[0m\n"
}

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

function ubuntuOrDebian() {
    if [[ "$(cat /etc/*-release | grep ^ID=)" == "ID=ubuntu" || "$(cat /etc/*-release | grep ^ID=)" == "ID=debian" ]]; then
        return 0
    else
        return 1
    fi
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
    printGreen "node is already installed."
else
    printYellow "Installing node."

    if [ -x "$(command -v apt-get)" ]; then
        if which curl >/dev/null ; then
            printYellow "Downloading via curl."
            curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        elif which wget >/dev/null ; then
            printYellow "Downloading via wget."
            wget -qO- https://deb.nodesource.com/setup_18.x | sudo -E bash -
        else
            printRed "Cannot download, neither wget nor curl is available."
            exit 1
        fi
        sudo apt-get update

        sudo apt-get install -y nodejs
    elif [ -x "$(command -v pacman)" ]; then
        sudo pacman -S nodejs

    elif [ -x "$(command -v pkg)" ]; then
        sudo pkg install node

    elif [ -x "$(command -v brew)" ]; then
        sudo brew install node

    else
        printRed "Unable to determine package manager for this system"
        exit 1
    fi

    if [ -x "$(command -v node)" ]; then
        printGreen "Node.js was installed successfully"
    else
        printRed "Node.js was not installed successfully"
    fi
fi


if which pnpm >/dev/null ; then
    printGreen "pnpm is already installed."
else
    printYellow "Installing pnpm."

    if which curl >/dev/null ; then
        printYellow "Downloading via curl."
        curl -fsSL https://get.pnpm.io/install.sh | sh -
    elif which wget >/dev/null ; then
        printYellow "Downloading via wget."
        wget -qO- https://get.pnpm.io/install.sh | sh -
    else
        printRed "Cannot download, neither wget nor curl is available."
        exit 1
    fi

    export PNPM_HOME="~/.local/share/pnpm"
    case ":$PATH:" in
        *":$PNPM_HOME:"*) ;;
        *) export PATH="$PNPM_HOME:$PATH" ;;
    esac

    printGreen "pnpm is installed."
fi

if which python3 >/dev/null ; then
    printGreen "python3 is already installed."
else
    printYellow "Installing python3."
    
    if [ -x "$(command -v apt-get)" ]; then
        sudo apt-get install python3 -y
    elif [ -x "$(command -v pacman)" ]; then
        sudo pacman -S python3
    elif [ -x "$(command -v pkg)" ]; then
        sudo pkg install python3
    elif [ -x "$(command -v brew)" ]; then
        sudo brew install python3
    else
        printRed "Unable to determine package manager for this system"
        exit 1
    fi

    printGreen "python3 is installed."
fi

function checkPip3() {
    if which pip3 >/dev/null ; then
        printGreen "pip3 is already installed."
        return 0
    elif which ~/.local/bin/pip3 >/dev/null ; then
        printGreen "pip3 is already installed."
        printYellow "adding ~/.local/bin to PATH"

        if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
            if cat ~/.bashrc | grep "# LOCAL_BIN_PATH" > /dev/null ; then
                printGreen "LOCAL_BIN_PATH is already in .bashrc"
                source ~/.bashrc
            else
                printYellow "adding LOCAL_BIN_PATH to .bashrc"
                echo "" >> ~/.bashrc
                echo "# LOCAL_BIN_PATH" >> ~/.bashrc
                echo "export PATH=\$PATH:\$HOME/.local/bin" >> ~/.bashrc
                source ~/.bashrc
            fi
        fi
        return 0
    else 
        return 1
    fi
}

if checkPip3 ; then
    printGreen "pip3 is already installed."
    printYellow "adding ~/.local/bin to PATH"

    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        if cat ~/.bashrc | grep "# LOCAL_BIN_PATH" > /dev/null ; then
            printGreen "LOCAL_BIN_PATH is already in .bashrc"
            source ~/.bashrc
        else
            printYellow "adding LOCAL_BIN_PATH to .bashrc"
            echo "" >> ~/.bashrc
            echo "# LOCAL_BIN_PATH" >> ~/.bashrc
            echo "export PATH=\$PATH:\$HOME/.local/bin" >> ~/.bashrc
            source ~/.bashrc
        fi
    fi
else
    printYellow "Installing pip3."

    if which curl >/dev/null ; then
        printYellow "Downloading via curl."
        curl -fsSL https://bootstrap.pypa.io/get-pip.py | python3 -
    elif which wget >/dev/null ; then
        printYellow "Downloading via wget."
        wget -qO- https://bootstrap.pypa.io/get-pip.py | python3 -
    else
        printRed "Cannot download, neither wget nor curl is available."
        exit 1
    fi

    if checkPip3 ; then
        printGreen "pip3 is installed."
    else
        printRed "failed to install pip3."
        printRed "Please install pip3 manually."
        exit 1
    fi
fi

printYellow "Installing dependencies."

pnpm run setup

pnpm install
pnpm install:api
pnpm install:web

printGreen "Dependencies are installed."
printYellow "Generating api-key secret"

SECRET=$(python3 -c "import os; import binascii; print(binascii.hexlify(os.urandom(32)))")
ALGORITHM="HS256"
substring=$(echo "$SECRET" | sed "s/'//g" | awk '{print $1}' | cut -c 2-)

if [[ -f api/.env ]]; then
    printYellow "api/.env exists, editing it."
    sed -i "s/secret=.*/secret=$substring/g" api/.env
    sed -i "s/algorithm=.*/algorithm=$ALGORITHM/g" api/.env
else
    printYellow "api/.env does not exist, creating it."
    echo "secret=$substring" > api/.env
    echo "algorithm=$ALGORITHM" >> api/.env
fi

printGreen "api-key secret is generated."
printGreen "Setup is complete."
printf "\n"
printGreen "Run 'pnpm deploy:web' to deploy the web server."
printGreen "Run 'pnpm start:api' to start the api server."

printf "\n\e[1m\e[33mDo you want to deploy the web server and start the api server?\e[0m" -n
read -p " (y/n): " -n 1 -r

if [[ $REPLY =~ ^[Yy]$ ]]
then
    printf "\n"
    pnpm deploy:web
    pnpm start:api
fi