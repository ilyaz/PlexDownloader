from xml.dom import minidom
import urllib
import os
import time
import hashlib
from ConfigParser import SafeConfigParser
import re
import socket
from urllib2 import Request, urlopen, quote
import base64
import uuid
import platform
from time import gmtime, strftime
import random
import string

def myPlexSignin(username,password):
	try:
		if os.path.isfile('token.txt'):
			with open('token.txt', 'r') as f:
  				authtoken = f.readline()
  			print "Using cached myPlex token."
  			return authtoken
		elif username != '' and password != '':
			print "Fetching myPlex authentication token."
			headers={}
			headers["Authorization"] = "Basic %s" % base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
			headers["X-Plex-Client-Identifier"] = quote(base64.encodestring(str(uuid.getnode())).replace('\n', ''))
			headers["X-Plex-Product"] = "Plex-Downloader"
			headers["X-Plex-Device"] = "Plex-Downloader"
			headers["X-Plex-Device-Name"] = socket.gethostname()
			headers["X-Plex-Platform"] = platform.system()
			headers["X-Plex-Client-Platform"] = platform.system()
			headers["X-Plex-Platform-Version"] = platform.version()
			headers["X-Plex-Provides"] = "controller"
			r = Request("https://plex.tv/users/sign_in.xml", data="", headers=headers)
			r = urlopen(r)

			compiled = re.compile("<authentication-token>(.*)<\/authentication-token>", re.DOTALL)
			authtoken = compiled.search(r.read()).group(1).strip()
			if authtoken != None:
				f = open('token.txt','w+')
				f.write(authtoken) # python will convert \n to os.linesep
				f.close() 
				return authtoken
				print "Successfully authenticated with myPlex!"
			else:
				print "Failed to login to myPlex!"
				return authtoken
		else:
			authtoken = ""

	except Exception, e:
		print "Failed to login to myPlex: %s" % str(e)