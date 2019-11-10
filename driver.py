import socket
import threading
import paxos
import network
import boot
import JSON            #Cusom msg formatter for JSON
import json
from queue import Queue


PORT   = 10000
NUMPIS = 3
OTHERPIS = NUMPIS-1

MY_PI = boot.getPiNum()

recvQueue = Queue()
sendQueue = Queue()

def mapResponse(msg):
	_json = json.loads(msg)
	
	src = _json["src"]

	#returns the sender
	return src, msg


def processNetworkData(recvQueue, sendQueue, socketList):
	while True:
		if not recvQueue.empty():
			msg = recvQueue.get()	
			print("Received message - ", msg)
			response = paxos.processNetworkData(msg)


			#TODO: Figure out way of mapping each message to its corresponding socket to send from
			if response is not None:
				for res in response:
					mappedRes = mapResponse(res) #Should be in the form (piNum, msg)
					sendQueue.put(mappedRes)
			

"""
	param1 listenSock: socket that should be continously listened on
	param2 msgQueue:   global queue that is shared between sockets that will contain all messages received on the process

	brief: Continuously listens on the socket and once received places the message in the global message queue
"""
def recvThread(listenSock, recvQueue):
	while True:
		msg = listenSock.recv(1024).decode('utf-8')
		recvQueue.put(msg)	




"""
	param1 socketList: list of uninitialized sockets to call connect on some IP

	brief: Continuously listens on the socket and once received places the message in the global message queue
"""
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
			connSock = socketList[amountConnected]				

			#If we can't connect we should throw an error and retry
			connSock.connect((deviceIP, PORT))				

			#Json Message and request Pi Num
			src = MY_PI
			msg = JSON.jsonMsg(src, None, state="REVEAL").encode('utf-8')
			connSock.send(msg)

			amountConnected += 1
		except Exception as e:
			print("EXCEPTION: ", e)
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
	
	#Start thread that handles receives
	threading.Thread(target=processNetworkData, args=(recvQueue, sendQueue, socketList)).start()

	#threading.Thread(target=sendThread, args=(sendQueue,)).start()
	#threading.Thread(target=establishMapping, args=(piToSocketMap)).start()

	while True:

		newConnection = mainSock.accept()[0]
		threading.Thread(target=recvThread,args=(newConnection, recvQueue)).start()

	mainSock.close()

if __name__ == '__main__': __main__()
