#!/bin/bash
echo "DEPENDENCY: getmac ... INSTALLING"
pip3 install getmac
echo "DEPENDENCY: getmac ... DONE"

export PATH="$PATH:/home/pi/.local/bin"
echo "PATH EXPORTED ... /home/pi/.local/bin"

echo "DEPENDENCY: Libbluetooth-dev ... INSTALLING"
sudo apt-get install libbluetooth-dev
echo "DEPENDENCY: Libbluetooth-dev ... DONE"


echo "DEPENDENCY: Pybluez ... INSTALLING"
pip3 install pybluez
echo "DEPENDENCY: Pybluez ... DONE"

eval `./install_dependencies.sh`
echo "EVAL COMPLETED ... ./install_dependencies.sh"
