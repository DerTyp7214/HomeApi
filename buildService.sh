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

sudo touch /etc/systemd/system/homeApi.service

sudo echo "[Unit]" >> /etc/systemd/system/homeApi.service
sudo echo "Description=Home API" >> /etc/systemd/system/homeApi.service
sudo echo "After=network.target" >> /etc/systemd/system/homeApi.service
sudo echo "" >> /etc/systemd/system/homeApi.service
sudo echo "[Service]" >> /etc/systemd/system/homeApi.service
sudo echo "User=$USER" >> /etc/systemd/system/homeApi.service
sudo echo "WorkingDirectory=$workingDirectory" >> /etc/systemd/system/homeApi.service
sudo echo "ExecStart=$startCommand" >> /etc/systemd/system/homeApi.service
sudo echo "" >> /etc/systemd/system/homeApi.service
sudo echo "[Install]" >> /etc/systemd/system/homeApi.service
sudo echo "WantedBy=multi-user.target" >> /etc/systemd/system/homeApi.service

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