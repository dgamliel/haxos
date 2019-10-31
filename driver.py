import socket
import os
import threading
import paxos
import network

PORT = 10000

def test(connection):
	print("Connection received from {}, {}".format(connection[0], connection[1]))
  

def tryConnection(socket):
	while True:
			openDevices = network.scanForPis()

			if len(openDevices) == 0:
				print("No available pis on the network... retrying")
				continue



			deviceIP = openDevices[0]
			print("Attempting to connect to", deviceIP, PORT)
			socket.connect((deviceIP, PORT))
			print("Failed to connect to pi... retrying")

def __main__():

	#Create main socket to listen to connections on 
	mainSock = socket.socket()	
	mainSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


	localIP = network.get_ip()
	print("localIP is ", localIP)
	mainSock.bind((localIP, PORT))
	mainSock.listen(10)

	sockets = [socket.socket() for i in range(5)]
	trySock = sockets[0]

	while True:
		newConnection = mainSock.accept()
		threading.Thread(target=test,args=(newConnection,)).start()

	mainSock.close()

if __name__ == '__main__': __main__()
