import configparser
import json
import os
import socket

def getPiNum():
    config = configparser.ConfigParser()
    config.read('config.ini')

    piNum = config['piNum']['number']
    return piNum

print(piNum)
