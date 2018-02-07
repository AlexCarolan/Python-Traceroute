import socket
import os
import sys
import struct
import time
import select
import binascii  


ICMP_ECHO_REQUEST = 8 #ICMP type code for echo request messages
ICMP_ECHO_REPLY = 0 #ICMP type code for echo reply messages

HOP_NUMBER = 0 # Current hop number
CURR_IP = "NULL" # IP adress of responder
RECIVED = 0 # Packets Recived
LOST = 0 # Packets Lost


def checksum(string): 
	csum = 0
	countTo = (len(string) // 2) * 2  
	count = 0

	while count < countTo:
		thisVal = ord(string[count+1]) * 256 + ord(string[count]) 
		csum = csum + thisVal 
		csum = csum & 0xffffffff  
		count = count + 2
	
	if countTo < len(string):
		csum = csum + ord(string[len(string) - 1])
		csum = csum & 0xffffffff 
	
	csum = (csum >> 16) + (csum & 0xffff)
	csum = csum + (csum >> 16)
	answer = ~csum 
	answer = answer & 0xffff 
	answer = answer >> 8 | (answer << 8 & 0xff00)
	
	if sys.platform == 'darwin':
		answer = socket.htons(answer) & 0xffff		
	else:
		answer = socket.htons(answer)

	return answer 
	
def receiveOnePing(icmpSocket, destinationAddress, timeSent):
	global HOP_NUMBER
	global CURR_IP
	global LOST
	global RECIVED
	
	# Wait for the socket to receive a reply
	# Once received, record time of receipt, otherwise, handle a timeout
	try:
		packet_data, address = icmpSocket.recvfrom(1024)
		recived = time.time()
	except:
		print("Hop " + str(HOP_NUMBER) + " Timed Out")
		LOST = LOST + 1
		return
	
	# Isolate address
	address = address[0]
	CURR_IP = address
	try:
		addressName, x, y = socket.gethostbyaddr(address)
	except:
		addressName = "NULL"
	
	# Compare the time of receipt to time of sending, producing the total network delay
	delay = recived - timeSent
	delay = round(delay * 1000.0, 3)
	
	RECIVED = RECIVED + 1
	
	# Print the result
	print("Hop " + str(HOP_NUMBER) + " Delay: " + str(delay) + " ms, IP Address: " + address + ", Host Name: " + addressName)
	
def sendOnePing(icmpSocket, destinationAddress):
	# Build the ICMP header
	header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, ICMP_ECHO_REPLY, 0, 1, 1)
	# Checksum ICMP packet using given function
	chkSum = checksum(header)
	# Insert checksum into packet
	packet = struct.pack("bbHHh", ICMP_ECHO_REQUEST, ICMP_ECHO_REPLY, chkSum, 1, 1)
	# Send packet using socket
	icmpSocket.send(packet)
	# Record time of sending
	timeSent = time.time()
	return timeSent
	

def doOnePing(destinationAddress, timeout): 
	global HOP_NUMBER
	# Create ICMP socket for send and recive
	icmp = socket.getprotobyname("icmp")
	sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
	recv_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
	sock.connect((destinationAddress, 80))
	recv_sock.settimeout(timeout)
	sock.setsockopt(socket.SOL_IP, socket.IP_TTL, HOP_NUMBER)
	# Call sendOnePing function
	timeSent = sendOnePing(sock, destinationAddress)
	# Call receiveOnePing function
	receiveOnePing(recv_sock, destinationAddress, timeSent)
	# Close ICMP sockets
	sock.close()
	recv_sock.close()
	
	
def ping(host):
	global HOP_NUMBER
	global CURR_IP
	
	timeout = int(input("Input the timeout value in seconds: "))
	
	# look up hostname, resolving it to an IP address
	ipAddress = socket.gethostbyname(host)
	# Call doOnePing function
	while(CURR_IP != ipAddress):
		HOP_NUMBER = HOP_NUMBER + 1
		doOnePing(ipAddress, timeout)
		time.sleep(1)
	# Continue this process until end is reached	
	
host = input("Input the adress of the site: ")
ping(host)

print("Unreachable Destinations: " + str(LOST))
print("Recived: " + str(RECIVED))



