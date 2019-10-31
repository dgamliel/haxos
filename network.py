from getmac import get_mac_address

import socket
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP



def scanForPis():
	pis = []
	prefix = '192.168.1.'
	for i in range(256):
		madeIP = prefix + str(i)
		mac = get_mac_address(ip=madeIP, network_request=True)

		if mac is not None and 'b8:27:eb' in mac:
			pi = madeIP
			pis.append(madeIP)

	return pis
