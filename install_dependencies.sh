#!/bin/bash
echo "DEPENDENCY: getmac ... INSTALLING"
pip3 install getmac
echo "DEPENDENCY: getmac ... DONE"
export PATH="$PATH:/home/pi/.local/bin"
echo "PATH EXPORTED ... /home/pi/.local/bin"
eval `./install_dependencies.sh`
echo "EVAL COMPLETED ... ./install_dependencies.sh"
