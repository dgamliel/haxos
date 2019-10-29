from getmac import get_mac_address

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
