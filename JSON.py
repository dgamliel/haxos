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

	messageList = message.split('{')
	
	retList = []

	for msg in messageList:
		if msg != '':
			msg = '{' + msg
			retList.append(msg)

	print(retList)
	return retList



