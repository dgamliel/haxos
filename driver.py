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
TOTAL_PIS_CONNECTED = 0

#ID of each PI
MY_PI = boot.getPiNum()

#Queues to share messages over send and receive
recvQueue = Queue()
sendQueue = Queue()

pVals = paxos.paxosValues()


socketMap = {}

def mapResponse(msg):
	_json = json.loads(msg)
	
	STATE = _json["state"]
	src   = _json["src"]
	dest  = _json["dest"]

	if STATE == "REVEAL":
		return src, msg
	return dest, msg


def processNetworkData(recvQueue, sendQueue, socketMap):

	pVals = paxos.paxosValues()

	while True:
		if not recvQueue.empty():
			msg = recvQueue.get()

			response = paxos.processNetworkData(pVals,msg)

			#Assumption: each message has already been mapped in recvThread
			if response is not None:
				for res in response:
					mappedRes = mapResponse(res) #Should be in the form (piNum, msg)
					sendQueue.put(mappedRes)

			else:
				print("Ignoring none message!")

#def sendThread(sendQueue, socketMap):
def sendThread(socketMap):
	"""
	param1 sendQueue: queue that contains global list of messages from all queues
	param2 socketMap: mapping of all piNumbers to their corresponding sockets

	Brief: Listens in on global queue of messages to be sent, maps the message to the correct socket and sends it
	"""

	global sendQueue

	while True:
		if not sendQueue.empty():

			mapped = False #Assume upon each send that our message is not mapped

			toSend = sendQueue.get()

			dest, msg = toSend
			dest = int(dest)

			print("dest", dest, "msg", msg)

			#Busy wait until we map the socket we want to send to
			sendToSock = socketMap[dest]


			sendToSock.send(msg.encode('utf-8'))



def recvThread(listenSock, recvQueue, socketMap):

	"""
	param1 listenSock: socket that should be continously listened on
	param2 msgQueue:   global queue that is shared between sockets that will contain all messages received on the process

	brief: Continuously listens on the socket and once received places the message in the global message queue
	"""

	global TOTAL_PIS_CONNECTED

	while True:

		msg = listenSock.recv(1024).decode('utf-8')

		#check that message has mapping, if not, we map in socketMapping

		_json = json.loads(msg)

		messageSender = int(_json["src"])

		if messageSender not in socketMap.keys():
			TOTAL_PIS_CONNECTED += 1
			socketMap[messageSender] = listenSock
			print("New pi added to map", socketMap)

		print("recv from", messageSender, "msg", msg)
		recvQueue.put(msg)	


def bcastConnect(socketList):
	"""
	param1 socketList: list of uninitialized sockets to call connect on some IP

	brief: Continuously listens on the socket and once received places the message in the global message queue

	Assumptions: Other procs listening for connections
	"""

	sendingRepeated=False #This is to check we don't send multiple all connected msgs
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

			if amountConnected == OTHERPIS:
				connected=True

		except Exception as e:
			print("EXCEPTION: ", e)
			print("Failed to connect to pi at {}... retrying".format(deviceIP))


	#After ensuring all pis are connected then we start paxos
	while not pVals.TOTAL_PIS_CONNECTED == OTHERPIS:
		pass

	print("INITIATING PAXOS")
	startPaxosMsgs = paxos.paxos(pVals)	
	for msg in startPaxosMsgs:
		sendQueue.put(msg)
	


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
	threading.Thread(target=processNetworkData, args=(recvQueue, sendQueue, socketMap)).start()

	#threading.Thread(target=sendThread, args=(sendQueue,socketMap)).start()
	threading.Thread(target=sendThread, args=(socketMap,)).start()

	while True:

		newConnection = mainSock.accept()[0]
		threading.Thread(target=recvThread,args=(newConnection, recvQueue, socketMap)).start()

	mainSock.close()

if __name__ == '__main__': __main__()
