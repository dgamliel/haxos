from boot import getPiNum
import threading
import json
from JSON import jsonMsg
#import queue


'''
# ballot = <Num, pid, depth of block>
# "An acceptor doesnot accept, prepare, or accept messages from a contending leader
# if the depth of the block being proposed is lower than the acceptor’s depth of
# its copy of the blockchain"
'''
#Paxos info
pid          = getPiNum()
ballot       = [0,pid]
acceptBallot = [0,0]
acceptVal    = ""
depth        = 0

#Maintaining paxos data as messages come in
acceptCountDict = {} #key=ballot, value = acceptCount
#sendQueue       = queue.Queue()

#This is what we will propose in phase II from leader
initialVal    = None
proposingBool = False
phaseTwoList  = []

#Connection configuration
#TODO: Fix for my current architecture

#Locks for concurrency
lock = threading.Lock()

#For timeouts
ackCount = 0

def startTimer():
	#After 5 seconds
	print('\nTimer started for 5 seconds!\n')
	sleep(5)
	if ackCount == 2:
		abortMsg = jsonMsg(name, name, state="ABORT")
		sendQueue.put(abortMsg)

#TODO: Rework with current architecture
def constantlyAccept(sock):
	while True:
		sock.accept()

#TODO: Rework with current architecture
#threading.Thread(target=constantlyAccept, args=(serv,)).start()


#ping other servers for blockchain
def requestUpdate():
	for dest in names: #send to all others
		_json = jsonMsg(name,dest,state="PING")
		sendQueue.put(_json)

#TODO: Rework for current processes 
def listenNetwork(conn):
	while True:
		msg = conn.networkRecv()
		for jsonD in msg:
			if jsonD!="":
				threading.Thread(target=processNetworkData, args=(jsonD,)).start()
				

#TODO: Rework for current architecture
def processNetworkData(msg):
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
	#print('[Server %s] Received from Network: %s\n' % (name, msg))

	#Load json msg and get state
	_json = json.loads(msg)
	state = _json["state"]

	if state == "PREPARE" :
		receivedBal = _json["ballot"]

		#Cannot accept smaller ballots in the future
		if receivedBal >= ballot:
			ballot[0] = receivedBal[0]
			dest = _json["src"]
			_json = jsonMsg(name,dest,state="ACK",ballot = receivedBal,acceptBallot=acceptBallot,acceptVal=acceptVal)	
			sendQueue.put(_json)



		#If bal smaller than myBal --> Don't respond
		else:
			lock.release()
			return
		
	elif state == "ACCEPT":

		receivedBal = _json["ballot"]
		receivedV = _json["blockString"]
		
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
				_json = jsonMsg(name,src,ballot=receivedBal,blockString=acceptVal,state="ACCEPT")
				#sendQueue.put(_json)
				lock.release()
				return _json

		#TODO: Set Majority to not be 3 but variable
		if acceptCount==3: #case (leader)

			messages=[]

			#Broadcast messages
			for dest in names:
				_json = jsonMsg(name,dest,ballot=receivedBal,x_y_coord=receivedV,state="DECIDE")
				messages.append(_json)

			#Send message to myself
			_json = jsonMsg(name,name,ballot=receivedBal,x_y_coord=receivedV,state="DECIDE")
			messages.append(_json)

			#remove block from transaction queue
			#only pop if proposing own value!!!!!!!!!!
			if(receivedV==initialVal):
				#transactions.pop(0)
				#transactions.pop(0)
				ackCount = 0

			#set proposing to false
			proposingBool=False

			#return the messages
			return messages

	#We have decided the value and will append the block to the blockchain
	elif state == "DECIDE": 

		# _variable indicates variable from the received JSON
		_blockString = _json["blockString"]

		#convert the string to a json object that has the block data
		_block = json.loads(_blockString)
		_depth = int(_block["blockDepth"])

		if _depth<=depth:
			#already recieved this block!!!!
			#IGNORE THAT MF THANG
			print("Ignoring repeated block")


			# #reset paxos vals for next round
			proposingBool = False
			acceptBallot = [0,0]
			acceptVal = ""
			ackCount = 0
			#call paxos to see if it should run
			paxos()



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
		if len(phaseTwoList)==3:

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
					pairBal = pair[0]
					highestBal = pairBal
					myVal = pairVal

			if myValChosen == True:
				myVal = initialVal


			#send accept, ballot,myVal to all
			for dest in names:
				_json = jsonMsg(name,dest,blockString=myVal,ballot=ballot,state="ACCEPT")
				sendQueue.put(_json)
			_json = jsonMsg(name,name,blockString=myVal,ballot=ballot,state="ACCEPT")
			sendQueue.put(_json)

	elif state == "PING":
		#load up each block in the chain and send it
		dest = _json["src"]


		_json = jsonMsg(name, dest, blockString, ballot=ballot, state="UPDATE")
		return [_json]
		#sendQueue.put(_json)

	elif state == "UPDATE":

		theirBallot = _json["ballot"]
		if theirBallot[0] > ballot[0]:
			ballot[0] = theirBallot[0]

		_block = stringToBlock(_json["blockString"])
		_depth = _block.header.blockDepth
		if _depth-depth==1:
				# print(_block)
				depth= _depth
				blockChain.add(_block)

	elif state == "ABORT":
		#Reset paxos values
		proposingBool = False
		acceptBallot  = [0,0]
		acceptVal     = ""
		ackCount      = 0
		
		#Remove transactions from the list
		#TODO: Consider what it means to drop an x_y_coord
		'''
		for i in range(2):
			transactions.pop(0)
		'''

		#serv.sendClient('Unable to complete transaction')

	
	elif state == "REVEAL":
		myId = getPiNum()
		msg  = jsonMsg(dest, src, acceptVal=myId, state="REVEAL_RESPONSE")

		#Return type should be a list
		return [msg]

	lock.release()


def paxos():
	
	global transactions
	global ballot
	global phaseTwoList
	global initialVal
	global acceptCountDict
	global sendQueue
	global proposingBool
	#Ready to add to blockchain if len>2 and not already trying to propose a block
	if(len(transactions)>=2 and not proposingBool):
		if not blockChain.verifyTransactions(transactions[0], transactions[1]):
			transactions.pop()
			transactions.pop()
			serv.sendClient("Invalid Transaction")
			return
		#reset paxos vals for next round
		acceptBallot = [0,0]
		acceptVal = ""
		# acceptCountDict = {}

		proposingBool = True #set the flag so can't call paxos again
		ballot[0]+=1

		phaseTwoList = [] #clearing the list so that previous ACKs are deleted


		"""
		prevHash = None
		if depth != 0:
			prevHash = createPrevHash(blockChain.chain[-1])
		else:
			prevHash = ""
		# prevHash = blockChain[-1].header.prevHash if depth != 0 else ""
		nonce = mineBlock(depth, transactions[0], transactions[1], prevHash)
		block = jsonBlock(transactions[0],transactions[1],depth+1,prevHash,nonce) #create the blockchain block
		"""
		initialVal = block #TODO: Figure out what this is supposed is supposed to be

		messages = []

		for dest in names: #send to all others
			_json = jsonMsg(name,dest,state="PREPARE",ballot=ballot)
			#sendQueue.put(_json)
			messages.append(_json)

		#send to self
		_json = jsonMsg(name,name,state="PREPARE",ballot=ballot)
		messages.append(_json)
		#sendQueue.put(_json)
			
		return messages

