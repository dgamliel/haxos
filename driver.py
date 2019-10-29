import socket
import os
import threading
import paxos
import network

PORT = 10000

def test(connection):
	connInfo = connection.gethostname()
	print("Connection received from {}".fmt(connInfo))
  

def tryConnection(socket, openDevices):
	try:
		deviceIP = openDevices[0]
		print("Attempting to connect to", deviceIp, PORT)
		socket.connect((deviceIP, PORT))
	except:
		print("Trying to connect to ", deviceIP)

def __main__():

	#Returns list of all other pis on the network
	openDevices = network.scanForPis()

	if len(openDevices) == 0:
		print("NO DEVICES FOUND")

	#Set up my listener socket
	mainSock = socket.socket()	
	localIP = socket.gethostbyname(socket.gethostname())
	mainSock.bind((localIP, PORT))
	mainSock.listen(10)

	sockets = [socket.socket() for i in range(5)]
	trySock = sockets[0]

	while True:
		threading.Thread(target=tryConnection, args=(trySock, openDevices)).start()
		newConnection = mainSock.accept()
		threading.Thread(target=test,args=(newConnection)).start()


	mainSock.close()

if __name__ == '__main__': __main__()
