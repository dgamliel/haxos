import socket
import os
import threading
import paxos
import network



PORT = 10000

def test(connection):
	connInfo = connection.gethostname()
	print("Connection received from {}".fmt(connInfo))


def __main__():

	#Returns list of all other pis on the network
	openDevices = network.scanForPis()

	#Set up my listener socket
	mainSock = socket.socket()	
	localIP = socket.gethostbyname(socket.gethostname())
	mainSock.bind((localIP, PORT))
	mainSock.listen(10)

	
	sockets = [socket.socket() for i in range(5)]
	
	#Dummy connection to see if it works
	tmpSock = sockets[0].connect((openDevices[0], PORT))


	while True:
		newConnection = mainSock.accept()
		threading.Thread(target=test,args=(newConnection)).start()


	mainSock.close()

if __name__ == '__main__': __main__()