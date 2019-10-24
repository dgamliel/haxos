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

	

	while True:
		newConnection = mainSock.accept()
		threading.Thread(target=test,args=(newConnection)).start()


	mainSock.close()

if __name__ == '__main__': __main__()
