import socket
import struct
import fcntl

#Get the IP mask
iface = "eth0"
_mask = socket.inet_ntoa(fcntl.ioctl(socket.socket(socket.AF_INET, socket.SOCK_DGRAM), 35099, struct.pack('256s', iface))[20:24])

#Get the local ip range 
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))

#Grab the prefix
loc_ip_prefix = s.getsockname()[0].split('.')[:2]
'.'.join(loc_ip_prefix)

mask = [~int(_byte) & 0xff for _byte in _mask.split('.')]

print(s.getsockname()[0])
print(_mask)
s.close()

