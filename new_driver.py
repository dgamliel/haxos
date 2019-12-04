### TODO: Figure out why X_Y_COORD doesn't propegate from prepare to accept/ack ###
import time
import socket
import threading
import paxos
import network
import boot
import JSON            #Cusom msg formatter for JSON
import math
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

#Set of other addresses
ipAddrs = set()

#Lock for concurrency
lock = threading.Lock()


#My IP
localIP = network.get_ip()
PORT    = 10000

#To be used in processNetworkData
me = localIP

'''
# ballot = <Num, pid, depth of block>
# "An acceptor doesnot accept, prepare, or accept messages from a contending leader
# if the depth of the block being proposed is lower than the acceptor’s depth of
# its copy of the blockchain"
'''
#Paxos info
pid          = boot.getPiNum()
ballot       = [0,pid]
acceptBallot = [0,0]
acceptVal    = ""
depth        = 0

#Maintaining paxos data as messages come in
acceptCountDict = {} #key=ballot, value = acceptCount

#This is what we will propose in phase II from leader
initialVal    = None
proposingBool = False
phaseTwoList  = []

#For timeouts
ackCount = 0

MAJORITY = math.ceil(NUMPIS/2)

def startTimer():
	#After 5 seconds
	print('\nTimer started for 10 seconds!\n')
	time.sleep(10)
	if ackCount == 2:
		abortMsg = jsonMsg(name, name, state="ABORT")
		sendQueue.put(abortMsg)

def getSocketFromMessage(msg):

    global sendMap

    _json = json.loads(msg)
    dest  = _json["dest"]

    return sendMap[dest]

def processNetworkData(msg):

    print("processNetworkData()::84 - Processing", msg)

    global lock
    lock.acquire()

    global ackCount
    global ballot
    global phaseTwoList
    global acceptBallot
    global acceptVal
    global acceptCountDict
    global sendQueue
    global transactions
    global proposingBool
    #global depth
    #global blockChain
    #global chainList
    #global chainsRecevied
    global me

    #Load json msg and get state
    _json = json.loads(msg)
    state = _json["state"]

    if state == "PREPARE" :
        receivedBal = _json["ballot"]

        #Cannot accept smaller ballots in the future
        if receivedBal >= ballot:
            #print("processNetworkData()::111 - Responding to prepare!")
            ballot[0] = receivedBal[0]
            dest  = _json["src"]
            coord = _json["x_y_coord"] 

            _json = JSON.jsonMsg(me,dest,state="ACK",ballot = receivedBal,acceptBallot=acceptBallot,acceptVal=coord, x_y_coord=coord)	
            sendQueue.put(_json)
            #print("processNetworkData()::121 - sendQueue", list(sendQueue.queue))



        #If bal smaller than myBal --> Don't respond
        else:
            #print("processNetworkData()::124 - Ignore smaller ballot")
            lock.release()
            return

    elif state == "ACCEPT":

        receivedBal = _json["ballot"]
        receivedV = _json["x_y_coord"]

        #Check if we received the ballot before
        #if first time receiving ballot --> set ballot count to 1
        #else --> increment ballot count
        if str(receivedBal) not in acceptCountDict.keys():
            acceptCountDict[str(receivedBal)] = 1

        else:
            acceptCountDict[str(receivedBal)] += 1

        acceptCount = acceptCountDict[str(receivedBal)]

        if acceptCount == 1: #case (not leader)

            #received ballot >= currentballot number, then we "commit" to that value
            if receivedBal[0] >= ballot[0]:

                acceptBallot = receivedBal
                acceptVal = receivedV

                src=  _json["src"]
                _json = JSON.jsonMsg(me,src,ballot=receivedBal,x_y_coord=acceptVal,state="ACCEPT")
                sendQueue.put(_json)
                lock.release()
                return
        
        #TODO: CHECK WHAT THIS COUNT SHOULD BE - I'M NOT ENTIRELY SURE USED TO BE 2
        if acceptCount==MAJORITY: #case (leader)
            for dest in ipAddrs:
                _json = JSON.jsonMsg(me,dest,ballot=receivedBal,x_y_coord=receivedV,state="DECIDE")
                sendQueue.put(_json)
            #TODO: Update self values so that we consider a message sent to ourselves

            #remove block from transaction queue
            #only pop if proposing own value!!!!!!!!!!
            if(receivedV==initialVal):
                ackCount = 0

            #set proposing to false
            proposingBool=False


    #We have decided the value and will append the block to the blockchain
    elif state == "DECIDE": 

        # _variable indicates variable from the received JSON
        x_y_coord = _json["x_y_coord"]

        #TODO: WRITE TO FILE
        with open('paxos.log', 'a+') as f:
            f.write(x_y_coord + "\n")
            f.close()

        #reset paxos vals for next round
        proposingBool = False
        acceptBallot = [0,0]
        acceptVal = ""
        ackCount = 0

        #call paxos to see if it should run
        startPaxos()



    elif state == "ACK":
        ackCount += 1
        if ackCount == 2:
            threading.Thread(target=startTimer, args=()).start()

        #Received from acceptor phase I --> leader phase II
        receivedVal = _json["acceptVal"]
        receivedBal = _json["acceptBallot"]

        #acceptPair <-- acceptBallot , acceptval
        acceptPair = [receivedBal,receivedVal]
        phaseTwoList.append(acceptPair)

        #Received from majority
        if len(phaseTwoList)==MAJORITY:

            #Vars to hold highest ballot and checking flags
            myValChosen = True
            highestBal = [-1,-1]
            myVal = None

            for pair in phaseTwoList:

                #case acceptor node has accepted value
                pairVal = pair[1]
                if(pairVal!=""):
                    myValChosen = False #We were not accepted as the leader. Need to restart

                    #find highestBallot
                    if(pair[0]>highestBal):
                        pairBal    = pair[0]
                        highestBal = pairBal
                        myVal      = pairVal

                if myValChosen == True:
                    myVal = initialVal


                #send accept, ballot,myVal to all
                for dest in ipAddrs:
                    _json = JSON.jsonMsg(me,dest,x_y_coord=myVal,acceptVal=myVal,ballot=ballot,state="ACCEPT")
                    sendQueue.put(_json)


    elif state == "ABORT":

        #Reset paxos values
        proposingBool = False
        acceptBallot  = [0,0]
        acceptVal     = ""
        ackCount      = 0



    lock.release()


    '''
    elif state == "PING":
    #load up each block in the chain and send it
    dest = _json["src"]

    #Send the entire blockchain to whoever pinged
    for block in blockChain.chain:
    txA   = block.transactionList[0]
    txB   = block.transactionList[1]
    depth = block.header.blockDepth
    _hash = block.header.hash
    nonce = block.header.nonce

    x_y_coord = jsonBlock(txA, txB, depth,_hash,nonce)
    _json = JSON.jsonMsg(name, dest, x_y_coord, ballot=ballot, state="UPDATE")
    sendQueue.put(_json)

    elif state == "UPDATE":

    theirBallot = _json["ballot"]
    if theirBallot[0] > ballot[0]:
    ballot[0] = theirBallot[0]

    _block = stringToBlock(_json["x_y_coord"])
    _depth = _block.header.blockDepth
    if _depth-depth==1:
    # print(_block)
    depth= _depth
    blockChain.add(_block)
    '''





def sendThread():

    global sendQueue

    while True:
        if not sendQueue.empty():
            message    = sendQueue.get()
            #print("sendThread()::293 - Sending", message)
            sendSocket = getSocketFromMessage(message) 


            sendSocket.send(message.encode('utf-8'))


def recvThread(recvSock):
    global recvQueue

    while True:

        recvMessage = recvSock.recv(1024).decode('utf-8')
        
        for message in JSON.splitDualMessage(recvMessage): 
            processNetworkData(message)

        #print("recvThread()::59 Received", recvMessage)

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
                        #print("SendMap", sendMap)
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

    print("waitRecvConnections(): DONE ... Able to receive messages from all pis")

def startPaxos():
    global sendQueue
    global sendMap
    global localIP

    me = localIP

    ballot[0] += 1

    for dest in sendMap.keys():
        sendMessage = JSON.jsonMsg(me,dest,state="PREPARE",ballot=ballot, x_y_coord = "<0.0, 1.1>")
        sendQueue.put(sendMessage)
        #sock = sendMap[dest]
        #sock.send(sendMessage.encode('utf-8'))

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

    startPaxos()


def __main__():

    global acceptedCount

    acceptor = socket.socket()	
    acceptor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    print("Listening is ", localIP, PORT)
    acceptor.bind((localIP, PORT))
    acceptor.listen(10)

    #### Start Threads ####
    threading.Thread(target=setup, args=()).start()
    threading.Thread(target=sendThread, args=()).start()


    while True:	

        #Get the new connection and immediately start receiving on it
        newConnection = acceptor.accept()[0]
        threading.Thread(target=recvThread, args=(newConnection,)).start()

        #Grab the remote IP from the socket
        remoteIP = newConnection.getpeername()[0]
        print("Connection received from IP", remoteIP)

        #Map remote IP to the socket we're going to listen on
        ipAddrs.add(remoteIP)
        recvMap[remoteIP] = newConnection 

        #print(recvMap)

        acceptedCount += 1		
		
if __name__ == '__main__': __main__()
