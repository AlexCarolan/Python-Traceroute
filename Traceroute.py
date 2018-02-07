import socket
import os
import sys
import struct
import time
import select
import binascii  


ICMP_ECHO_REQUEST = 8 #ICMP type code for echo request messages
ICMP_ECHO_REPLY = 0 #ICMP type code for echo reply messages

HOP_NUMBER = 0
CURR_IP = "NULL"


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
	
	# 1. Wait for the socket to receive a reply
	# 2. Once received, record time of receipt, otherwise, handle a timeout
	try:
		packet_data, address = icmpSocket.recv(1024)
		recived = time.time()
	except:
		print("Time Out")
		return
	
	# Isolate address
	address = address[0]
	CURR_IP = address
	try:
		addressName = gethostbyaddr(address)
	except:
		addressName = "NULL"
	
	# 3. Compare the time of receipt to time of sending, producing the total network delay
	delay = recived - timeSent
	delay = round(delay * 1000.0, 3)
	
	# Print the result
	print("Hop " + str(HOP_NUMBER) + " Delay: " + str(delay) + " ms, IP Address: " + address + ", Host Name: " + addressName)
	
def sendOnePing(icmpSocket, destinationAddress):
	# 1. Build ICMP header
	header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, ICMP_ECHO_REPLY, 0, 1, 1)
	# 2. Checksum ICMP packet using given function
	chkSum = checksum(header)
	# 3. Insert checksum into packet
	packet = struct.pack("bbHHh", ICMP_ECHO_REQUEST, ICMP_ECHO_REPLY, chkSum, 1, 1)
	# 4. Send packet using socket
	icmpSocket.send(packet)
	# 5. Record time of sending
	timeSent = time.time()
	return timeSent
	

def doOnePing(destinationAddress, timeout): 
	global HOP_NUMBER
	# 1. Create ICMP socket
	icmp = socket.getprotobyname("icmp")
	sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
	#sock.setsockopt(socket.SOL_IP, socket.IP_TTL, HOP_NUMBER)
	sock.connect((destinationAddress, 80))
	sock.settimeout(timeout)
	# 2. Call sendOnePing function
	timeSent = sendOnePing(sock, destinationAddress)
	# 3. Call receiveOnePing function
	receiveOnePing(sock, destinationAddress, timeSent)
	# 4. Close ICMP socket
	sock.close()
	# 5. Return total network delay
	
def ping(host):
	global HOP_NUMBER
	global CURR_IP
	
	timeout = int(input("Input the timeout value in seconds: "))
	
	# 1. Look up hostname, resolving it to an IP address
	ipAddress = socket.gethostbyname(host)
	# 2. Call doOnePing function
	while(CURR_IP != ipAddress):
		HOP_NUMBER = HOP_NUMBER + 1
		doOnePing(ipAddress, timeout)
		time.sleep(1)
	# 3. Print out the returned delay
	# 4. Continue this process until stopped	
	
ping("www.lancaster.ac.uk")



