if which pnpm >/dev/null ; then
    echo "pnpm is already installed."
else
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
    source /home/toor/.bashrc
fi

pnpm install
pnpm install:api
pnpm install:web