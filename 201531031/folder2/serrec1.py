from threading import Thread
from random import randint
import os
import socket
import hashlib
from os.path import isfile, join
from os import listdir
import re
import stat
import time
from stat import *
from collections import *


class Server(Thread):
	def __init__(self):
		Thread.__init__(self)

	def run(self):
		port = 40000
		port2 = 30000
		s = socket.socket()
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
		host = ""


		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		s.bind((host, port))
		s.listen(5)

		# filename = raw_input("Enter file to share:")
		# print 'Server listening....'
                    

		def executeIndex(command):
			answer=''
			if command[1] == 'longlist':
			    files = os.listdir(os.curdir)
			    answer += ('Index'+' File'+'Size'+'Type'+'Timestamp') + '\n' + ('-----'+' ----' + ' ----' + ' ----' + ' ---------') + '\n'
			    for num,file in enumerate(files):
			    	fileType = 'file'
			    	if os.path.isdir(file): fileType = 'directory'
			        answer += str( str(num+1)+') ' + file + ' ' + str(os.stat(file).st_size) + ' ' + fileType + ' ' + str(os.stat(file).st_mtime) + '\n')

			if command[1] == 'shortlist':
			    lowLim,HighLim = int(command[2]), int(command[3])
			    allTimes, size = [], []
			    getFiles = os.listdir(os.curdir)
			    for file in getFiles:
			        c=os.stat(file)
			        allTimes.append(int(c.st_mtime))
			        size.append(int(c.st_size))
			    g = 0
			    answer += ('Index'+' File'+' Size'+' Type') + '\n' + ('-----'+' ----'+' ----'+' ----') + '\n'
			    for num,file in enumerate(getFiles):
			        fileType = 'file'
			        if os.path.isdir(file): fileType = 'directory'
			        if allTimes[num] > lowLim and allTimes[num] < HighLim:
			            answer += str(str(g+1)+') ' + file + ' ' + str(size[num]) + ' ' + fileType + '\n')
			            g+=1
			if command[1] == 'regex':
			    typeoOfFile = command[2]
			    g = 0
			    answer += ('Index' + ' File' + ' Size' + ' Type') + '\n' + ('-----' + ' ----' + ' ----' + ' ----') + '\n'
			    for num,file in enumerate(os.listdir(os.curdir)):
			        if re.search(typeoOfFile, file):
			            c=os.stat(file)
			            fileType = 'file'
			            if os.path.isdir(file): fileType = 'directory'
			            answer += str(str(g+1) + ')' + ' ' + os.path.join(os.curdir, file) + ' ' + str(c.st_size) + ' ' + fileType + '\n')
			            g+=1
			return answer

		def executeHash(command):
			answer = ''
			if command[1] == 'verify':
			    fileName = command[2]
			    answer += ('Checksum ' + 'Last modified time') + '\n' + ('--------' + ' ---- --------- ----') + '\n'
			    hash_md5 = hashlib.md5()
			    if not os.path.isdir(fileName):
			        with open(fileName, "rb") as f:
			            for chunk in iter(lambda: f.read(4096), b""):
			                hash_md5.update(chunk)
			        answer += str(hash_md5.hexdigest() + ' ' +  str(os.stat(fileName).st_mtime)) + '\n'

			if command[1] == 'checkall':
			    answer += ('Index' + ' Filename' + ' Checksum' + ' Last modified time') + '\n' + ('-----' + ' --------' + ' --------' + ' ---- --------- ----') + '\n'
			    for num,fileName in enumerate(os.listdir(os.curdir)):
			        hash_md5 = hashlib.md5()
			        if not os.path.isdir(fileName):
			            with open(fileName, "rb") as f:
			                for chunk in iter(lambda: f.read(4096), b""):
			                    hash_md5.update(chunk)
			            answer += str(str(num + 1)+')' + ' ' + fileName + ' ' + hash_md5.hexdigest() + ' ' + str(os.stat(fileName).st_mtime) + '\n')
			return answer
		def executeDownload(command):
			answer = ''
			x = hashlib.md5()
			fileName = command[2]
			conn.send(oct(os.stat(fileName)[ST_MODE])[-3:])
			if command[1] == 'TCP':
			    f = open(fileName,'rb')
			    l = f.read(1024)
			    while (l):
			        if not l: 
			            break
			        conn.send(l)
			        time.sleep(0.1)
			        x.update(l)
			        conn.send(str(hashlib.md5(l).hexdigest()))
			        time.sleep(0.1)
			        l = f.read(1024)
			    f.close()
			    time.sleep(0.1)
			    conn.send('File finish')
			elif command[1] == 'UDP':
			    f = open(fileName,'rb')
			    l = f.read(1024)
			    while (l):
			        if not l: 
			            break
			        sock.sendto(l,(host,port2))
			        time.sleep(0.1)
			        l = f.read(1024)
			    f.close()
			    time.sleep(0.1)
			    sock.sendto('File finish',(host,port2))
			    hash_md5 = hashlib.md5()
			    with open(fileName, "rb") as f:
			        for chunk in iter(lambda: f.read(4096), b""):
			            hash_md5.update(chunk)
			    conn.sendto(hash_md5.hexdigest(), (host,port2))

	    
		def autoDownload():
			for fileName in os.listdir(os.curdir):
			    conn.send(fileName + ' ' + str(os.stat(fileName).st_mtime))
			    time.sleep(0.1)
			conn.send('Bye!')

		def runAll(command):
			if command[0] == 'index':
			    return executeIndex(command)
			if command[0] == 'hash':
			    return executeHash(command)
			if command[0] == 'download':
			    executeDownload(command)
			if command[0] == 'autoDownload':
			    autoDownload()


		currTime = prevTime = time.time()
		standardTime = 5


		conn, addr = s.accept()
		while True:
		    prevTime = time.time()
		    command = conn.recv(1024)
		    print '>>>', command
		    command = command.split()
		    print command
		    if command:
		        if command[0] != 'download' and command[0] != 'autoDownload': conn.send(runAll(command))
		        else: runAll(command)
		    else: break
		    if abs(currTime - prevTime) >= standardTime:
		        currTime = prevTime


		conn.close()

class Reciever(Thread):
	def __init__(self):
		Thread.__init__(self)

	def run(self):
		s = socket.socket()             
		host = ""
		port = 60000    
		port2 = 50000                
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
		sock.bind((host, port2))
		m = defaultdict()

		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.connect((host, port))
		currTime = prevTime = time.time()
		standardTime = 5
		run = ''


		while True:
			flag = 0
			her = 0
			prevTime = time.time()
			if abs(currTime - prevTime) >= standardTime:
				# print 'Entered'
				currTime = prevTime
				s.send('autoDownload')
				mTime2=defaultdict(float)
				while True:
					mTime = s.recv(1024)
					if  mTime == 'Bye!' : break
					if mTime == '': continue
					mTime = mTime.split()
					mTime2[mTime[0]] = float(mTime[1])
				mTime1=defaultdict(float)
				for fileName in os.listdir(os.curdir):
					mTime1[fileName] = (os.stat(fileName).st_mtime)
				for i in mTime2:
					if mTime2[i] > mTime1[i]:
						print 'Downloading!',i
						run = 'download TCP ' + i
						s.send(run)
						run = run.split()
						if(run[0] == 'download'):
							with open(run[2], 'wb') as f:
								permissions = int(s.recv(1024),8)
								while True:
									if run[1] == 'TCP':
										data = s.recv(1024)
										time.sleep(0.1)
										if data == 'File finish':
											if flag == 1: break
											else: print 'Download finished!'
											break
										hashVal = s.recv(1024)
										time.sleep(0.1)								
										if str(hashlib.md5(data).hexdigest()) != hashVal: 
											flag = 1 
									f.write(data)
							os.chmod(run[2],permissions)
							if flag == 1: print 'Some error occurred!'
							f.close()		
			
			print '>>>',
			run = raw_input()
			cmnd = run.split()
			if cmnd[0] == 'index' or cmnd[0] == 'hash' or cmnd[0] == 'download':
				if cmnd[0] == 'index':
					if not (cmnd[1] == 'longlist' or cmnd[1] == 'shortlist' or cmnd[1] == 'regex'): 
						her = 1
						print 'Invalid argument!'
				elif cmnd[0] == 'hash':
					if not (cmnd[1] == 'checkall' or cmnd[1] == 'verify'): 
						her = 1
						print 'Invalid argument!'
				elif cmnd[0] == 'download':
					if not (cmnd[1] == 'TCP' or cmnd[1] == 'UDP'): 
						her = 1
						print 'Invalid argument!'
				if her == 0:
					# print 4
					s.send(run)
					run = run.split()
					data = ''
					c=hashlib.md5()
					if(run[0] == 'download'):
						permissions = int(s.recv(1024),8)
						with open(run[2], 'wb') as f:
							while True:
								if run[1] == 'TCP':
									data = s.recv(1024)
									if data == 'File finish':
										if flag == 1: break
										print 'Download finished!'
										break
									hashVal = s.recv(1024)
									if str(hashlib.md5(data).hexdigest()) != hashVal: 
										flag = 1 
								elif run[1] == 'UDP':
									data , adr = sock.recvfrom(1024)					
									if data == 'File finish':
										print 'Download finished!'
										break
								f.write(data)
						if run[1] == 'UDP':
							hashFile = s.recv(1024) 
							hash_md5 = hashlib.md5()
							with open(run[2], "rb") as f:
								for chunk in iter(lambda: f.read(4096), b""):
									hash_md5.update(chunk)
							if hash_md5.hexdigest() != hashFile: print 'Some error occurred!'
						if flag == 1: print 'Some error occurred!'

						os.chmod(run[2],permissions)
						f.close()		
					# elif(run[0] == 'download1'):
					# 	with open(run[1], 'wb') as f:
					# 		while True:
					# 			data, adr = sock.recvfrom(1024)
					# 			if data == 'File finish':
					# 				print 'Download finished!'
					# 				break
					# 			f.write(data)
					# 	f.close()		
					else:
						print s.recv(1024)
			else:
				print 'Not a valid command!'



if __name__ == '__main__':

	reciever = Reciever()
	server = Server()

	# Start running the threads!
	server.start()
	time.sleep(10)
	reciever.start()

	# Wait for the threads to finish...
	server.join()
	reciever.join()

	print('Main Terminating...')
