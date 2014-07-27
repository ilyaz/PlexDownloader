#!/usr/bin/env python
# Author: Ilyaz <>
# URL: https://github.com/ilyaz/PlexDownloader
#
# This file is part of PlexDownloader.
#
# PlexDownlaoder is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PlexDownloader is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PlexDownloader.  If not, see <http://www.gnu.org/licenses/>.
#

from xml.dom import minidom
import urllib
import os
import time
from ConfigParser import SafeConfigParser
import re
import socket
from urllib2 import Request, urlopen, quote
import base64
import uuid
import platform
from time import gmtime, strftime

parser = SafeConfigParser()
parser.read('user.ini')

sleepTime = parser.get('general', 'sleeptime')
sleepTime = int(sleepTime)
url = parser.get('general', 'plexurl')

myplexstatus = parser.get('myplex', 'status')
myplexusername = parser.get('myplex', 'username')
myplexpassword = parser.get('myplex', 'password')

tvshowid = parser.get('tvshows', 'plexid')
tvfile = parser.get('tvshows', 'tvfile')
tvtype = parser.get('tvshows', 'tvtype')
tvlocation = parser.get('tvshows', 'tvlocation')

movieid = parser.get('movies', 'plexid')
movielocation = parser.get('movies', 'movielocation')
moviefile = parser.get('movies', 'moviefile')

plextoken=""

print "PlexDownloader - v0.01"

def myPlexSignin(username,password):
    try:

        if username != '' and password != '':
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
                return authtoken
                print "Successfully authenticated with myPlex!"
            else:
                print "Failed to login to myPlex!"
                return authtoken
        else:
            authtoken = ""

    except Exception, e:
        print "Failed to login to myPlex: %s" % str(e)


def epDownloader(show,season,episode,container,link,eptitle):
	epfile=urllib.URLopener()
	if not os.path.exists(tvlocation+show):
		os.makedirs(tvlocation+show)

	print "Downloading "+ show + " Season "+season+" Episode "+episode+"..."

	if not os.path.isfile(tvlocation+show+"/"+show+" - "+season+"x"+episode+" - "+eptitle+"."+container):
		epfile.retrieve(link,tvlocation+show+"/"+show+" - "+season+"x"+episode+" - "+eptitle+"."+container)
	else:
		print "File already exists. Skipping episode."

def mvDownloader(moviefull,container,link):
	mvfile=urllib.URLopener()
	if not os.path.exists(movielocation+moviefull):
		os.makedirs(movielocation+moviefull)

	print "Downloading "+ moviefull + "..."

	if not os.path.isfile(movielocation+moviefull+"/"+moviefull+"."+container):
		mvfile.retrieve(link,movielocation+moviefull+"/"+moviefull+"."+container)
	else:
		print "File already exists. Skipping movie."

def tvShowSearch():
	tvopen = open(tvfile,"r")
	tvread = tvopen.read()
	tvlist= tvread.split("\n")
	tvopen.close()
	print str(len(tvlist)) + " TV Shows Found in Your Wanted List..."
	if myplexstatus=="enable":
		tvhttp=url+"/library/sections/"+tvshowid+"/all"+"?X-Plex-Token="+plextoken
	else:
		tvhttp=url+"/library/sections/"+tvshowid+"/all"		

	website = urllib.urlopen(tvhttp)
	xmldoc = minidom.parse(website)
	itemlist = xmldoc.getElementsByTagName('Directory') 
	print str(len(itemlist)) + " Total TV Shows Found"
	for item in itemlist:
		tvkey = item.attributes['key'].value
		tvtitle = item.attributes['title'].value
		if tvtitle in tvlist:
			print tvtitle + " Found in Wanted List"
			if myplexstatus=="enable":
				seasonhttp=url+tvkey+"?X-Plex-Token="+plextoken
			else:
				seasonhttp=url+tvkey
			seasonweb = urllib.urlopen(seasonhttp)
			xmlseason = minidom.parse(seasonweb)
			seasonlist = xmlseason.getElementsByTagName('Directory')
			totalseasons =  len(seasonlist)
			for season in seasonlist:
				seasontitle= season.attributes['title'].value
				if (seasontitle != "All episodes"):
					if (tvtype=="all"):
						seasonkey= season.attributes['key'].value
						seasonindex= season.attributes['index'].value
						if myplexstatus=="enable":
							episodehttp=url+seasonkey+"?X-Plex-Token="+plextoken
						else:
							episodehttp=url+seasonkey
						episodeweb=urllib.urlopen(episodehttp)
						xmlepisode=minidom.parse(episodeweb)
						episodelist=xmlepisode.getElementsByTagName('Video')
						for episode in episodelist:
							episodekey = episode.attributes['key'].value
							episodeindex = episode.attributes['index'].value
							episodetitle = episode.attributes['title'].value
							partindex = episode.getElementsByTagName('Part')
							for partitem in partindex:
								downloadkey = partitem.attributes['key'].value
								downloadcontainer = partitem.attributes['container'].value
							print tvtitle + " Season "+ seasonindex + " Episode " + episodeindex
							if myplexstatus=="enable":
								eplink=url+downloadkey+"?X-Plex-Token="+plextoken
							else:
								eplink=url+downloadkey							
							epDownloader(tvtitle,seasonindex,episodeindex,downloadcontainer,eplink,episodetitle)
					elif (tvtype=="recent"):
						if (totalseasons==1 and seasontitle=="Season 1"):
							seasonkey= season.attributes['key'].value
							seasonindex= season.attributes['index'].value
							if myplexstatus=="enable":
								episodehttp=url+seasonkey+"?X-Plex-Token="+plextoken
							else:
								episodehttp=url+seasonkey
							episodeweb=urllib.urlopen(episodehttp)
							xmlepisode=minidom.parse(episodeweb)
							episodelist=xmlepisode.getElementsByTagName('Video')
							for episode in episodelist:
								episodekey = episode.attributes['key'].value
								episodeindex = episode.attributes['index'].value
								episodetitle = episode.attributes['title'].value
								partindex = episode.getElementsByTagName('Part')
								for partitem in partindex:
									downloadkey = partitem.attributes['key'].value
									downloadcontainer = partitem.attributes['container'].value
								print tvtitle + " Season "+ seasonindex + " Episode " + episodeindex
								if myplexstatus=="enable":
									eplink=url+downloadkey+"?X-Plex-Token="+plextoken
								else:
									eplink=url+downloadkey	
								epDownloader(tvtitle,seasonindex,episodeindex,downloadcontainer,eplink,episodetitle)
						elif (totalseasons>1 and seasontitle=="Season "+str(totalseasons-1)):
							seasonkey= season.attributes['key'].value
							seasonindex= season.attributes['index'].value
							if myplexstatus=="enable":
								episodehttp=url+seasonkey+"?X-Plex-Token="+plextoken
							else:
								episodehttp=url+seasonkey
							episodeweb=urllib.urlopen(episodehttp)
							xmlepisode=minidom.parse(episodeweb)
							episodelist=xmlepisode.getElementsByTagName('Video')
							for episode in episodelist:
								episodekey = episode.attributes['key'].value
								episodeindex = episode.attributes['index'].value
								episodetitle = episode.attributes['title'].value
								partindex = episode.getElementsByTagName('Part')
								for partitem in partindex:
									downloadkey = partitem.attributes['key'].value
									downloadcontainer = partitem.attributes['container'].value
								print tvtitle + " Season "+ seasonindex + " Episode " + episodeindex
								if myplexstatus=="enable":
									eplink=url+downloadkey+"?X-Plex-Token="+plextoken
								else:
									eplink=url+downloadkey	
								epDownloader(tvtitle,seasonindex,episodeindex,downloadcontainer,eplink,episodetitle)
						else:
							print "Ignoring "+tvtitle+" Season."
				else:
					print "Skipping all leaves."
		else:
			print tvtitle + " Not Found in Wanted List."


def movieSearch():
	movieopen = open(moviefile,"r")
	movieread = movieopen.read()
	movielist= movieread.split("\n")
	movieopen.close()
	print str(len(movielist)) + " Movies Found in Your Wanted List..."

	if myplexstatus=="enable":
		moviehttp=url+"/library/sections/"+movieid+"/all"+"?X-Plex-Token="+plextoken
	else:
		moviehttp=url+"/library/sections/"+movieid+"/all"
	website = urllib.urlopen(moviehttp)
	xmldoc = minidom.parse(website)
	itemlist = xmldoc.getElementsByTagName('Video') 
	print str(len(itemlist)) + " Total Movies Found"
	for item in itemlist:
		movietitle = item.attributes['title'].value
		movieyear = item.attributes['year'].value
		moviename = movietitle + " ("+movieyear+")"
		if moviename in movielist:
			print moviename
			mediaindex = item.getElementsByTagName('Media')
			for mediaitem in mediaindex:
				moviecontainer = mediaitem.attributes['container'].value
			partindex = item.getElementsByTagName('Part')
			for partitem in partindex:
				moviekey = partitem.attributes['key'].value
				if myplexstatus=="enable":
					movieurl=url+moviekey+"?X-Plex-Token="+plextoken
				else:
					movieurl=url+moviekey
			mvDownloader(moviename,moviecontainer,movieurl)
		else:
			print moviename + " Not Found in Wanted List."

while True:
	if myplexstatus=="enable":
		plextoken = myPlexSignin(myplexusername,myplexpassword)
	if myplexstatus=="enable" and plextoken=="":
		print "Failed to login to myPlex. Please disable myPlex or enter your correct login."
		exit()
	try:
		tvShowSearch()
		movieSearch()
		print "Plex Download completed at "+ strftime("%Y-%m-%d %H:%M:%S")
		print "Sleeping "+str(sleepTime)+" Seconds..."
		time.sleep(sleepTime)
	except: 
		print "Something went wrong"
		print "Plex Download failed at "+ strftime("%Y-%m-%d %H:%M:%S")
		print "Retrying in "+str(sleepTime)+" Seconds..."
		time.sleep(sleepTime)
