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

printf "\n\e[33mThis script will install node, npm, pnpm, mongodb, python3, and pip3.\nDo you wish to continue?\e[0m" -n
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

    if which curl >/dev/null ; then
        printYellow "Downloading via curl."
        curl -fsSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -
    elif which wget >/dev/null ; then
        printYellow "Downloading via wget."
        wget -qO- https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -
    else
        printRed "Cannot download, neither wget nor curl is available."
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
        printRed "pip3 is not installed."
    fi
fi

function addMongoRepo() {
    MONGO_VERSION=6.0
    currentDirectory=$(pwd)

    if [ -x "$(command -v lsb_release)" ]; then
        if [ "$(lsb_release -is)" == "Ubuntu" ]; then
            printGreen "Ubuntu detected."
            DISTRO="ubuntu"
            DISTRO_NAME=$(lsb_release -cs)
        elif [ "$(lsb_release -is)" == "Debian" ]; then
            printGreen "Debian detected."
            DISTRO="debian"
            DISTRO_NAME=$(lsb_release -cs)
        else
            printRed "Unsupported Linux distribution."
            exit 1
        fi
    else
        printRed "Unsupported Linux distribution."
        exit 1
    fi

    sudo apt-get update
    sudo apt-get install gnupg -y
    
    sudo mkdir -p /etc/apt/keyrings
    

    if which curl >/dev/null ; then
        printYellow "Downloading via curl."
        curl -fsSL https://www.mongodb.org/static/pgp/server-${MONGO_VERSION}.asc | sudo gpg --dearmor -o /etc/apt/keyrings/mongodb-${MONGO_VERSION}.gpg
    elif which wget >/dev/null ; then
        printYellow "Downloading via wget."
        wget -qO- https://www.mongodb.org/static/pgp/server-${MONGO_VERSION}.asc | sudo gpg --dearmor -o /etc/apt/keyrings/mongodb-${MONGO_VERSION}.gpg
    else
        printRed "Cannot download, neither wget nor curl is available."
        exit 1
    fi
    
    cd /etc/apt/sources.list.d/
    sudo touch mongodb-org-${MONGO_VERSION}.list
    
    echo "deb [arch=amd64,arm64 signed-by=/etc/apt/keyrings/mongodb-${MONGO_VERSION}.gpg] https://repo.mongodb.org/apt/${DISTRO} ${DISTRO_NAME}/mongodb-org/${MONGO_VERSION} multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-${MONGO_VERSION}.list
    sudo apt-get update

    cd $currentDirectory
}

if which mongod >/dev/null ; then
    printGreen "mongodb is already installed."
else
    if [[ "$(cat /etc/*-release | grep ^ID=)" == "ID=ubuntu" || "$(cat /etc/*-release | grep ^ID=)" == "ID=debian" ]]; then
        printYellow "Installing mongodb."

        addMongoRepo
        sudo apt-get install -y mongodb-org
        sudo apt-get install -y mongodb-org-shell
        sudo systemctl start mongod

        printGreen "mongodb is installed."
    else
        printRed "mongodb is not installed and this script does not support your OS. If your OS can install mongodb, install it and run this script again."
        exit 1
    fi
fi

if which mongosh >/dev/null ; then
    printGreen "mongosh is already installed."
else
    if [[ "$(cat /etc/*-release | grep ^ID=)" == "ID=ubuntu" || "$(cat /etc/*-release | grep ^ID=)" == "ID=debian" ]]; then
        printYellow "Installing mongosh."
        
        addMongoRepo
        sudo apt-get install -y mongodb-org-shell

        printGreen "mongosh is installed."
    else
        printRed "mongosh is not installed and this script does not support your OS. If your OS can install mongosh, install it and run this script again."
        exit 1
    fi
fi

if ! nc -zvv localhost 27017 2>&1 | grep -q "succeeded!"
then
    printYellow "mongodb is not running, starting it."
    sudo systemctl start mongod
    
    count=0
    while ! nc -zvv localhost 27017 2>&1 | grep -q "succeeded!"; do
        printYellow "mongodb is not running, waiting 5 seconds."
        sleep 5
        count=$((count+1))
        if [ $count -eq 10 ]; then
            printRed "mongodb is not running, exiting."
            exit 1
        fi
    done
else
    printGreen "mongodb is running."
fi

if [[ $(mongosh --eval "db.getMongo()" --quiet) == mongodb:* ]]; then
    printGreen "mongodb is running."

    if [[ $(mongosh --eval "db.getMongo().getDBNames().indexOf('web')" --quiet) != *-1 ]]; then
        printGreen "database 'web' exists."

        if [[ $(mongosh web --eval "db.getCollectionNames().indexOf('config')" --quiet) != *-1 ]]; then
            printGreen "collection 'config' exists."
        else
            printYellow "collection 'config' does not exist, creating it."
            mongosh web --eval "db.createCollection('config')" --quiet
        fi
    else
        printYellow "database 'web' does not exist, creating it."
        mongosh web --eval "db.createCollection('config')" --quiet
    fi
else
    printRed "mongodb is not running."
    exit 1
fi

printYellow "Installing dependencies."

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
printf "\n"
printYellow "Note: to use pnpm you need to run 'source ~/.bashrc' or restart your terminal."