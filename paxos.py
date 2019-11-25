from boot import getPiNum #Get ID
import threading          #Concurrency control     
import json               #Strings to JSON objects, etc
from JSON import jsonMsg  #Craft Json MSG's
from math import ceil     #Used to determine majority

'''
# ballot = <Num, pid, depth of block>
# "An acceptor doesnot accept, prepare, or accept messages from a contending leader
# if the depth of the block being proposed is lower than the acceptor’s depth of
# its copy of the blockchain"
'''

'''
class PaxosValues():
	
	def __init__(self):
'''

NUMPIS = 3
OTHERPIS = NUMPIS-1

#Paxos info
pid          = getPiNum()
ballot       = [0,pid]
acceptBallot = [0,0]
acceptVal    = ""
depth        = 0

#Maintaining paxos data as messages come in
acceptCountDict = {} #key=ballot, value = acceptCount

#This is what we will propose in phase II from leader
initialVal    = None
proposingBool = False

class paxosValues:
	def __init__(self):

		#Paxos info
		self.pid          = getPiNum()
		self.ballot       = [0,pid]
		self.acceptBallot = [0,0]
		self.acceptVal    = ""
		self.depth        = 0

		#Maintaining paxos data as messages come in
		self.acceptCountDict = {} #key=ballot, value = acceptCount

		#This is what we will propose in phase II from leader
		self.initialVal    = None
		self.proposingBool = False

		#For timeouts
		self.ackCount = 0

		self.phaseTwoList = []

		self.TOTAL_PIS_CONNECTED = 0


#Locks for concurrency
lock = threading.Lock()



def startTimer():
	#After 5 seconds
	print('\nTimer started for 5 seconds!\n')
	sleep(5)
	if ackCount == 2:
		abortMsg = jsonMsg(name, name, state="ABORT")
		sendQueue.put(abortMsg)



#TODO: Rework for current architecture
def processNetworkData(pVals,msg):
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

	#Convert msg string to json and get its contents
	_json = json.loads(msg)
	state = _json["state"]
	src  = _json["src"]
	dest = _json["dest"]
	#receivedBal = _json["ballot"] 

	if state == "PREPARE" :
		receivedBal = _json["ballot"]

		#Cannot accept smaller ballots in the future
		if receivedBal >= pVals.ballot:
			pVals.ballot[0] = receivedBal[0]
			dest = _json["src"]
			_json = jsonMsg(name,dest,state="ACK", ballot = receivedBal, acceptBallot=acceptBallot,acceptVal= pVals.acceptVal)	
			return (dest, _json)
			#sendQueue.put(_json)


		#If bal smaller than myBal --> Don't respond
		else:
			lock.release()
			return
		
	elif state == "ACCEPT":

		receivedBal = _json["ballot"]
		#TODO:Received val should be x_y_coord
		receivedV = _json["x_y_coord"]
		
		#Check if we received the ballot before
		#if first time receiving ballot --> set ballot count to 1
		#else --> increment ballot count
		if str(receivedBal) not in pVals.acceptCountDict.keys():
			pVals.acceptCountDict[str(receivedBal)] = 1

		else:
			pVals.acceptCountDict[str(receivedBal)] += 1

		#Grab the accept count
		acceptCount = pVals.acceptCountDict[str(receivedBal)]

		if acceptCount == 1: #case (not leader)

			#received ballot >= currentballot number, then we "commit" to that value
			if receivedBal[0] >= ballot[0]:

				acceptBallot = receivedBal
				acceptVal = receivedV

				src=  _json["src"]
				_json = jsonMsg(name,src,ballot=receivedBal,blockString=acceptVal,state="ACCEPT")
				#sendQueue.put(_json)
				lock.release()
				return [_json]

		#TODO: Set Majority to not be 3 but variable
		if acceptCount==3: #case (leader)
		#if acceptCount == pVals.majority

			messages=[]

			#Broadcast messages
			for dest in names:
				_json = jsonMsg(name,dest,ballot=receivedBal,x_y_coord=receivedV,state="DECIDE")
				messages.append(_json)

			#Send message to myself
			#TODO: MODIFY VALUES SO THAT WE CAN FIGURE OUT WHEN TO DECIDE
			#_json = jsonMsg(name,name,ballot=receivedBal,x_y_coord=receivedV,state="DECIDE")
			messages.append(_json)

			#remove block from transaction queue
			#only pop if proposing own value!!!!!!!!!!
			if receivedV == pVals.initialVal:
				ackCount = 0

			#set proposing to false
			proposingBool=False

			#return the messages
			return messages

	#We have decided the value and will append the block to the blockchain
	elif state == "DECIDE": 

		x_y_coord = _json["x_y_coord"]

		# _variable indicates variable from the received JSON
		#_blockString = _json["blockString"]

		#convert the string to a json object that has the block data
		#_block = json.loads(_blockString)
		#_depth = int(_block["blockDepth"])

	
		"""
		TODO: Configure for x_y_coordinate
		if _depth<=depth:
			#already recieved this block!!!!
			#IGNORE THAT MF THANG
			print("Ignoring repeated block")
		"""

		#TODO: Write to file containing paxos values


		# #reset paxos vals for next round
		pVals.proposingBool = False
		pVals.acceptBallot = [0,0]
		pVals.acceptVal = ""
		pVals.ackCount = 0
		#call paxos to see if it should run
		paxos(pVals)

		

	elif state == "ACK":
		pVals.ackCount += 1

		if pVals.ackCount == 2:
			threading.Thread(target=startTimer, args=()).start()

		#Received from acceptor phase I --> leader phase II
		receivedVal = _json["acceptVal"]
		receivedBal = _json["acceptBallot"]

		#acceptPair <-- acceptBallot , acceptval
		acceptPair = [receivedBal,receivedVal]
		pVals.phaseTwoList.append(acceptPair)

		#Received from majority
		#if len
		if len(pVals.phaseTwoList)==3:

			#Vars to hold highest ballot and checking flags
			myValChosen = True
			highestBal = [-1,-1]

			#Init myVal to be none to be sent out soon
			myVal = None

			for pair in phaseTwoList:
				#case acceptor node has accepted value
				pairVal = pair[1]
				if pairVal != "":
					myValChosen = False #We were not accepted as the leader. Need to restart

				#find highestBallot
				if(pair[0]>highestBal):
					pairBal = pair[0]
					highestBal = pairBal
					myVal = pairVal

			if myValChosen == True:
				myVal = pVals.initialVal


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
		if theirBallot[0] > pVals.ballot[0]:
			pVals.ballot[0] = theirBallot[0]

		"""
		_block = stringToBlock(_json["blockString"])
		_depth = _block.header.blockDepth
		if _depth-depth==1:
				# print(_block)
				depth= _depth
				blockChain.add(_block)
		"""

	elif state == "ABORT":
		#Reset paxos values
		proposingBool = False
		acceptBallot  = [0,0]
		acceptVal     = ""
		ackCount      = 0
		
		#Remove transactions from the list
		#NOTE: Consider what it means to drop an x_y_coord
		'''
		for i in range(2):
			transactions.pop(0)
		'''

		#Drop the values from the paxos class
		return None

		#serv.sendClient('Unable to complete transaction')

	
	elif state == "REVEAL":
		myId = getPiNum()
		msg  = jsonMsg(myId, src, acceptVal=None, state="REVEAL_RESPONSE")

		#Return type should be a list
		return [msg]

	elif state == "ALL_CONNECTED":
		pVals.TOTAL_PIS_CONNECTED += 1
		return None

	lock.release()


	#global phaseTwoList
def paxos(pVals):
	
	global transactions
	global ballot
	global initialVal
	global acceptCountDict
	global sendQueue
	global proposingBool

	#Ready to add to blockchain if len>2 and not already trying to propose a block
	if not proposingBool:

		#reset paxos vals for next round
		pVals.acceptBallot = [0,0]
		pVals.acceptVal = ""
		# acceptCountDict = {}

		pVals.proposingBool = True #set the flag so can't call paxos again
		pVals.ballot[0]+=1

		pVals.phaseTwoList = [] #clearing the list so that previous ACKs are deleted


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

		

		initialVal = 'AAAAAAAAAAAA' #TODO: Figure out what this is supposed is supposed to be

		messages = []

		for i in range(1, NUMPIS+1): #send to all others
			dest = i
			if i != pid:
				_json = jsonMsg(pid,dest,state="PREPARE",ballot=ballot)
				messages.append((i,_json))

		"""
		#send to self
		_json = jsonMsg(name,name,state="PREPARE",ballot=ballot)
		sendQueue.put(_json)
		"""

		return messages

