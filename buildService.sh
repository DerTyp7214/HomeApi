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

if which systemd > /dev/null; then
    printGreen "Systemd is installed"
else
    printYellow "Installing systemd"
    
    sudo apt-get update
    sudo apt-get install systemd -y
fi

uvicornLocation=$(which uvicorn)
workingDirectory=$(pwd)

startCommand="$uvicornLocation api.main:app --host 0.0.0.0"

printGreen "Creating service file"

echo "[Unit]" >> homeApi.service
echo "Description=Home API" >> homeApi.service
echo "After=network.target" >> homeApi.service
echo "" >> homeApi.service
echo "[Service]" >> homeApi.service
echo "User=$USER" >> homeApi.service
echo "WorkingDirectory=$workingDirectory" >> homeApi.service
echo "ExecStart=$startCommand" >> homeApi.service
echo "" >> homeApi.service
echo "[Install]" >> homeApi.service
echo "WantedBy=multi-user.target" >> homeApi.service

read -p "Do you want to install the service? (y/n) " -n 1 -r

echo

if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    printRed "Aborting"
    exit 1
fi

sudo mv homeApi.service /etc/systemd/system/homeApi.service

printGreen "Reloading daemon"

sudo systemctl daemon-reload

printGreen "Enabling service"

sudo service homeApi enable

printGreen "Starting service"

sudo service homeApi start

printGreen "Service started"

printGreen "Service status"

sudo service homeApi status

printGreen "Service logs"

sudo journalctl -u homeApi.service -f

printGreen "Done"