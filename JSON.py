import json
#Wanted to use JSON block for input to JSON msg

def jsonMsg(src, dest, x_y_coord = "",ballot = "",acceptVal = "", acceptBallot = "",state=""):
    _json = {
        "src":src,
        "dest":dest,
        "ballot": ballot,
        "acceptVal": acceptVal,
        "acceptBallot": acceptBallot,
        "x_y_coord": x_y_coord,
        "state":state #prepare,accept,decide,ack,reveal, reveal_response
    }

    return json.dumps(_json)

def splitDualMessage(message):

	splitInd = 0

	#Find if we received a concatenated message
	for i in range(1, len(message)):
		if message[i] == '{':
			splitInd = i
			break

	if splitInd != 0:
		mes1 = message[:splitInd]
		mes2 = message[splitInd:]

		retList = [mes1, mes2]
		print("splitDualMessage 32: ", retList)
		return retList 

	retList = [message]
	print("splitDualMessage 36: ", retList)
	return [message]


