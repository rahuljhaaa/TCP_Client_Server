#!/usr/bin/python
from collections import deque
import os
import socket               
import sys                 
import threading 
import keyboard           
import time                  
import configparser         
from JSONClass import *     
from log import *           
from GPIO import *   
from config import *         
exitFlag = 0     

queue_obj = deque()

def Request_SocketListen(threadName, hostname, port):
  try:
	global queue_obj
	# Create a TCP/IP socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# Bind the socket to the port
	server_address = (hostname, port)
	sock.bind(server_address)
	# Listen for incoming connections
	sock.listen(1)
	print("Socket Listen starting up on Server IP:" +str(hostname)+", Request Port:"+str(port))
	ClsLogger.WriteLog("TCP Server Request Port", "I", "Socket Listen starting up on Server IP:" +str(hostname)+", Request Port:"+str(port))
	ObjGPIO=GPIOLayer()
	# Wait for a connection
	while True:
		
		ClsLogger.WriteLog("TCP Server Request Port", "I", "******************************************************************")
		ClsLogger.WriteLog("TCP Server Request Port", "I", "Waiting for a Request from Client @ Server IP:" +str(hostname)+", Request Port:"+str(port))
		connection, client_address = sock.accept() # Wait for a connection
		try:
			# Receive the data in small chunks and retransmit it
			#while True:
			data = connection.recv(1024)
			RecvdJSON = data.decode('utf-8')
			RecvdJSON = RecvdJSON.replace("'",'"')
			Status = str(ClsJSON.ReadJSON(RecvdJSON ,"STATUS"))
			ClsLogger.WriteLog("TCP Server", "I", " Request JSON recived from client. JSON=>"+str(RecvdJSON))

			if(Status.upper()=="WRITE"):         
				ResJSON = ObjGPIO.GPIO_Write(RecvdJSON)
				queue_obj.append(ResJSON)


			if(Status.upper()=="READ"):         
				ResJSON = ObjGPIO.GPIO_Read(RecvdJSON)
				queue_obj.append(ResJSON)

			ClsLogger.WriteLog('TCP aapending queue', 'I',"Response Append" + str(queue_obj))

			

		except Exception as e:
			ClsLogger.WriteLog('TCP Server', 'E', str(e) +" " + str(server_address))
			connection.close()

		finally:
			connection.close()

  except KeyboardInterrupt:
	ClsLogger.WriteLog('TCP Server', 'I', "Closing Socket - Server Port .")
	try:
		connection.close()
		sock.close()
	except:
		pass
 
  except Exception as e:
	ClsLogger.WriteLog('TCP Server', 'E', str(e) +" " + str(server_address))
	try:
		connection.close()
		sock.close()
	except:
		pass

  finally:
	# Clean up the scoket
	try:
		connection.close()
		sock.close()
	except:
		pass


def Response_SocketListen(threadName, hostname, port):
  try:
	global queue_obj
	# Create a TCP/IP socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# Bind the socket to the port
	server_address = (hostname, port)
	sock.bind(server_address)
	# Listen for incoming connections
	sock.listen(1)
	print("\nSocket Listen starting up on Server IP:" +str(hostname)+", ResponsePort:"+str(port))
	ClsLogger.WriteLog("TCP Server - Response Port", "I", "Socket Listen starting up on Server IP:" +str(hostname)+", Response Port:"+str(port))
	# Wait for a connection
	while True:
		
		ClsLogger.WriteLog("TCP Server - Response Port", "I", "******************************************************************")
		ClsLogger.WriteLog("TCP Server - Response Port", "I", "Waiting for a Request from Client @ Server IP:" +str(hostname)+", Response Port:"+str(port))
		connection, client_address = sock.accept() # Wait for a connection
		try:
			# Receive the data in small chunks and retransmit it
			#while True:
			ReqJson = queue_obj.popleft()
			data = connection.recv(1024).decode('utf-8')
			connection.send(str(ReqJson).encode('utf-8'))

			ClsLogger.WriteLog('TCP Server', 'I', "After queue operation data is " + str(ReqJson))
			ClsLogger.WriteLog('TCP Server', 'I', "Data recived from client " + str(data))
			
			
		except Exception as e:
			ClsLogger.WriteLog('TCP Server', 'E', str(e) +" " + str(server_address))
			connection.close()

		finally:
			connection.close()

  except KeyboardInterrupt:
	ClsLogger.WriteLog('TCP Server', 'I', "Closing Socket - Server Port .")
	try:
		connection.close()
		sock.close()
	except:
		pass
 
  except Exception as e:
	ClsLogger.WriteLog('TCP Server', 'E', str(e) +" " + str(server_address))
	try:
		connection.close()
		sock.close()
	except:
		pass

  finally:
	# Clean up the scoket
	try:
		connection.close()
		sock.close()
	except:
		pass
   
try:

   ClsLogger.WriteLog("TCP Server", "I", "*******************TCP Server Application - Starting....*******************")

   try:
	  os.system("fuser -k "+str(requestport)+"/tcp")
	  os.system("fuser -k "+str(responseport)+"/tcp")
   except Exception as e:
	raise
   finally:
	time.sleep(1)
	pass

   
   # Create new threads
   threads = [ ]
   t1 = threading.Thread(target=Request_SocketListen, args=("Server-RequestPort", serverip, int(requestport)))
   threads.append(t1)
   t1.start()

   t2 = threading.Thread(target=Response_SocketListen, args=("Server-ResponsePort", serverip, int(responseport)))
   threads.append(t2)
   t2.start()

   for onethread in threads:
	  onethread.join()

except Exception as e:
	ClsLogger.WriteLog('TCP Server', 'E', "Error while starting TCP server application. Please try again!." + str(e))

finally:
	pass

