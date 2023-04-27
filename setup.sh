#!/bin/bash

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