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

    export PNPM_HOME="~/.local/share/pnpm"
    case ":$PATH:" in
        *":$PNPM_HOME:"*) ;;
        *) export PATH="$PNPM_HOME:$PATH" ;;
    esac
fi

if which python3 >/dev/null ; then
    echo "python3 is already installed."
else
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
fi


pnpm install
pnpm install:api
pnpm install:web