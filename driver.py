import socket
import os
import threading
#import paxos
import network

PORT   = 10000
NUMPIS = 3
OTHERPIS = NUMPIS-1

def test(connection):
	print("Connection received from {}, {}".format(connection[0], connection[1]))
  

def bcastConnect(socketList):

	connected=False
	amountConnected = 0

	while not connected:
			openDevices = network.scanForPis()

			print("----- Attempting to connect to {} of {} other pis -----".format(amountConnected, OTHERPIS))

			#Attempt to connect to all pis
			try:
				deviceIP = openDevices[amountConnected]
				print("Attempting to connect to", deviceIP, PORT)
				socketList[amountConnected].connect((deviceIP, PORT))
				amountConnected += 1
			except Exception as e:
				print(e)
				print("Failed to connect to pi at {}... retrying".format(deviceIP))

			if amountConnected == OTHERPIS:
				connected=True

	print("ALL CONNECTIONS ACHIEVED")

def __main__():

	#Create main socket to listen to connections on 
	mainSock = socket.socket()	
	mainSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


	localIP = network.get_ip()
	print("localIP is ", localIP)
	mainSock.bind((localIP, PORT))
	mainSock.listen(10)

	socketList = [socket.socket() for i in range(OTHERPIS)]

	#Start attempting to connect to all pis
	threading.Thread(target=bcastConnect, args=(socketList,)).start()


	while True:

		newConnection = mainSock.accept()
		threading.Thread(target=test,args=(newConnection,)).start()

	mainSock.close()

if __name__ == '__main__': __main__()
