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
        echo "export PATH=$PATH:$HOME/.local/bin" >> ~/.bashrc
        source ~/.bashrc
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