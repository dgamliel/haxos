import time
import socket
import threading
import paxos
import network
import boot
import JSON            #Cusom msg formatter for JSON
import json
from queue import Queue


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

#Maps to map IP to corresponding send/recv socket
recvMap = {}
sendMap = {}

pVals = paxos.paxosValues()

#Map the IP to the socket we need to send on
socketMap = {}

#My IP
localIP = network.get_ip()
PORT   = 10000

def sendThread():
    print("sendThread called!")
    return

def recvThread():
    print("recvThread called!")
    return

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
                        sendMap[remoteIP] = sock
                        print("SendMap", sendMap)
                        remoteConnected = True
                    except:
                        time.sleep(1)
                        pass

    print("connectSend(): DONE ... Able to send messages to all pis")

def waitRecvConnections():
	global acceptedCount 
	global TOTAL_PIS_CONNECTED 

	while acceptedCount != OTHERPIS:
		continue


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
    time.sleep(10)          #Extra buffer time to let all other people connect

    print("ALL CONNECTIONS RECEIVED - NOW NEED TO IMPLEMENT MESSAGE SENDING")


def __main__():

    global acceptedCount

    acceptor = socket.socket()	
    acceptor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    print("Listening is ", localIP, PORT)
    acceptor.bind((localIP, PORT))
    acceptor.listen(10)

    #### Start Threads ####
    threading.Thread(target=setup, args=()).start()

    while True:	
        newConnection = acceptor.accept()[0]

        #Map remote IP to the socket we're going to listen on
        remoteIP = newConnection.getpeername()[0]
        print("Connection received from IP", remoteIP)
        recvMap[remoteIP] = newConnection 

        print(recvMap)

        acceptedCount += 1		
		
if __name__ == '__main__': __main__()
