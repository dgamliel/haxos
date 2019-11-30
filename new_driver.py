import time
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

acceptedCount = 0

sendSockets = [socket.socket() for i in range(OTHERPIS)]

#ID of each PI
MY_PI = boot.getPiNum()

#Queues to share messages over send and receive
recvQueue = Queue()
sendQueue = Queue()

pVals = paxos.paxosValues()

#Map the IP to the socket we need to send on
socketMap = {}

def connectSend(openDevices, sendSockets):

	#Connect to all other pis found on the network
	for remoteSock in range(OTHERPIS):
		remoteIP = openDevices[remoteSock]  #open devices contains ip addresses
		sock     = sendSockets[remoteSock]  #Grab the socket to connect

		#Try attempting to the socket. On fail, retry
		remoteConnected = False
		while not remoteConnected:
			try:
				sock.connect((remoteIP, PORT))
				remoteConnected = True
			except:
				pass

def waitRecvConnections():
	global acceptedCount 
	global TOTAL_CONNECTION_COUNT

	while acceptedCount != OTHERPIS:
		continue


def waitTotalConnections():
    print("DONE")
    return


#This process will occurr before we send any messages
def setup():
	
    connected=False

    while not connected:
        openDevices = network.scanForPis()

        #We have not found any devices so scan again
        if len(openDevices) != OTHERPIS:
            print("Waiting for all pis to come up")
            time.sleep(1)
            continue

        connected = True

    #Wait for other pis to come up
    time.sleep(10)	

    #Attempt to connect to all of them
    connectSend(openDevices, sendSockets) #Attempt to connect to all our remotes

    waitRecvConnections()  #Wait until we have all our connections received
    print("ALL CONNECTIONS RECEIVED - NOW NEED TO IMPLEMENT MESSAGE SENDING")
    waitTotalConnections() #Send a message to all other pis that are listening, 


def __main__():

    global acceptedCount

    acceptor = socket.socket()	
    acceptor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    localIP = network.get_ip()
    print("Listening is ", localIP, PORT)
    acceptor.bind((localIP, PORT))
    acceptor.listen(10)

    #### Start Threads ####
    threading.Thread(target=setup, args=()).start()

    while True:	
        newConnection = acceptor.accept()[0]
        acceptedCount += 1		
		
if __name__ == '__main__': __main__()
