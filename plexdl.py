#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

parser = SafeConfigParser()
parser.read('user.ini')

import subprocess

webstatus = parser.get('webui','status')
webport = parser.get('webui','port')
if webstatus=="enable":
	print "Starting PlexDownloader Web Manager..."
	subprocess.Popen(["python", "webui.py", webport])

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
tvsync = parser.get('tvshows', 'fullsync')
tvactive = parser.get('tvshows', 'active')
tvdelete = parser.get('tvshows', 'autodelete')
tvunwatched= parser.get('tvshows','unwatched')

tvtranscode= parser.get('tvtranscode','active')
tvheight = parser.get('tvtranscode','height')
tvwidth = parser.get('tvtranscode','width')
tvbitrate = parser.get('tvtranscode','maxbitrate')
tvquality = parser.get('tvtranscode','videoquality')

movietranscode = parser.get('movietranscode','active')
movieheight = parser.get('movietranscode','height')
moviewidth = parser.get('movietranscode','width')
moviebitrate = parser.get('movietranscode','maxbitrate')
moviequality = parser.get('movietranscode','videoquality')

movieid = parser.get('movies', 'plexid')
movielocation = parser.get('movies', 'movielocation')
moviefile = parser.get('movies', 'moviefile')
moviesync = parser.get('movies', 'fullsync')
movieactive = parser.get('movies', 'active')
movieunwatched = parser.get('movies','unwatched')

musicid = parser.get('music', 'plexid')
musiclocation = parser.get('music', 'musiclocation')
musicfile = parser.get('music', 'musicfile')
musicsync = parser.get('music', 'fullsync')
musicactive = parser.get('music', 'active')

pictureid = parser.get('pictures', 'plexid')
picturelocation = parser.get('pictures', 'picturelocation')
picturefile = parser.get('pictures', 'picturefile')
picturesync = parser.get('pictures', 'fullsync')
pictureactive = parser.get('pictures', 'active')

#random_data = os.urandom(128)
#plexsession = hashlib.md5(random_data).hexdigest()[:16]
plexsession=str(uuid.uuid4())
socket.setdefaulttimeout(180)

plextoken=""

print "PlexDownloader - v0.03"

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

def mvTranscoder(moviefull,container,link,moviemetadata):
	container = "mp4"
	clientuid = uuid.uuid4()
	clientid = clientuid.hex[0:16]
	plexproduct = "Plex-Downloader"
	plexdevice = "Plex-Downloader"
	plexsession = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(16))
	devicename = socket.gethostname()
	plexplatform = platform.system()
	clientplatform = platform.system()
	platformversion = platform.version()
	plexprovides = "controller"
	if myplexstatus=="enable":
		link = url+"/video/:/transcode/universal/start?path=http%3A%2F%2F127.0.0.1%3A32400%2Flibrary%2Fmetadata%2F"+moviemetadata+"&mediaIndex=0&partIndex=0&protocol=http&offset=0.000&fastSeek=1&directPlay=0&directStream=1&videoQuality="+moviequality+"&videoResolution="+moviewidth+"x"+movieheight+"&maxVideoBitrate="+moviebitrate+"&subtitleSize=100&audioBoost=100&session="+plexsession+"&X-Plex-Client-Identifier="+clientid+"&X-Plex-Product=Plex+Web&X-Plex-Device=OSX&X-Plex-Platform=Chrome&X-Plex-Platform-Version=36.0&X-Plex-Version=2.2.3&X-Plex-Device-Name=Plex+Web+(Chrome)&X-Plex-Token="+plextoken
		print "Transcode URL: "+link
	else:
		link = url+"/video/:/transcode/universal/start?path=http%3A%2F%2F127.0.0.1%3A32400%2Flibrary%2Fmetadata%2F"+moviemetadata+"&mediaIndex=0&partIndex=0&protocol=http&offset=0.000&fastSeek=1&directPlay=0&directStream=1&videoQuality="+moviequality+"&videoResolution="+moviewidth+"x"+movieheight+"&maxVideoBitrate="+moviebitrate+"&subtitleSize=100&audioBoost=100&session="+plexsession+"&X-Plex-Client-Identifier="+clientid+"&X-Plex-Product=Plex+Web&X-Plex-Device=OSX&X-Plex-Platform=Chrome&X-Plex-Platform-Version=36.0&X-Plex-Version=2.2.3&X-Plex-Device-Name=Plex+Web+(Chrome)"
		print "Transcode URL: "+link
	mvfile=urllib.URLopener()
	moviefull = re.sub(r'[\\/:"*?<>|"]+',"",moviefull)
	if not os.path.exists(movielocation+moviefull):
		os.makedirs(movielocation+moviefull)

	print "Downloading transcoded "+ moviefull + "..."

	if not os.path.isfile(movielocation+moviefull+"/"+moviefull+"."+container):
		try:
			mvfile.retrieve(link,movielocation+moviefull+"/"+moviefull+"."+container)
		except:
			print "Something went wrong transcoding this movie... Deleting and retrying on next movie scan!"
			os.remove(movielocation+moviefull+"/"+moviefull+"."+container)			
	else:
		print "File already exists. Skipping movie transcode."

def tvTranscoder(show,season,episode,container,link,eptitle,tvmetadata):
	container = "mp4"
	plexproduct = "Plex-Downloader"
	plexdevice = "Plex-Downloader"
	devicename = socket.gethostname()
	plexplatform = platform.system()
	clientplatform = platform.system()
	platformversion = platform.version()
	plexsession = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(16))
	clientuid = uuid.uuid4()
	clientid = clientuid.hex[0:16]	
	plexsession = "z9fja0pznf40anzd"
	plexprovides = "controller"
	if myplexstatus=="enable":
		link = url+"/video/:/transcode/universal/start?path=http%3A%2F%2F127.0.0.1%3A32400%2Flibrary%2Fmetadata%2F"+tvmetadata+"&mediaIndex=0&partIndex=0&protocol=http&offset=0&fastSeek=1&directPlay=0&directStream=1&videoQuality="+tvquality+"&videoResolution="+tvwidth+"x"+tvheight+"&maxVideoBitrate="+tvbitrate+"&subtitleSize=100&audioBoost=100&session="+plexsession+"&X-Plex-Client-Identifier="+clientid+"&X-Plex-Product=Plex+Web&X-Plex-Device=OSX&X-Plex-Platform=Chrome&X-Plex-Platform-Version=36.0&X-Plex-Version=2.2.3&X-Plex-Device-Name=Plex+Web+(Chrome)&X-Plex-Token="+plextoken
		print "Transcode URL: "+link
	else:
		link = url+"/video/:/transcode/universal/start?path=http%3A%2F%2F127.0.0.1%3A32400%2Flibrary%2Fmetadata%2F"+tvmetadata+"&mediaIndex=0&partIndex=0&protocol=http&offset=0&fastSeek=1&directPlay=0&directStream=1&videoQuality="+tvquality+"&videoResolution="+tvwidth+"x"+tvheight+"&maxVideoBitrate="+tvbitrate+"&subtitleSize=100&audioBoost=100&session="+plexsession+"&X-Plex-Client-Identifier="+clientid+"&X-Plex-Product=Plex+Web&X-Plex-Device=OSX&X-Plex-Platform=Chrome&X-Plex-Platform-Version=36.0&X-Plex-Version=2.2.3&X-Plex-Device-Name=Plex+Web+(Chrome)"
		print "Transcode URL: "+link
	epfile=urllib.URLopener()
	show = re.sub(r'[\\/:"*?<>|"]+',"",show)
	eptitle = re.sub(r'[\\/:"*?<>|"]+',"",eptitle)
	if not os.path.exists(tvlocation+show):
		os.makedirs(tvlocation+show)

	print "Downloading transcoded "+ show + " Season "+season+" Episode "+episode+"..."

	if not os.path.isfile(tvlocation+show+"/"+show+" - "+season+"x"+episode+" - "+eptitle+"."+container):
		try:
			epfile.retrieve(link,tvlocation+show+"/"+show+" - "+season+"x"+episode+" - "+eptitle+"."+container)
		except:
			print "Something went wrong transcoding this episode... Deleting and retrying on next episode scan!"
			os.remove(tvlocation+show+"/"+show+" - "+season+"x"+episode+" - "+eptitle+"."+container)
	else:
		print "File already exists. Skipping episode transcode."

def epDownloader(show,season,episode,container,link,eptitle):
	epfile=urllib.URLopener()
	show = re.sub(r'[\\/:"*?<>|"]+',"",show)
	eptitle = re.sub(r'[\\/:"*?<>|"]+',"",eptitle)
	if not os.path.exists(tvlocation+show):
		os.makedirs(tvlocation+show)

	print "Downloading "+ show + " Season "+season+" Episode "+episode+"..."

	if not os.path.isfile(tvlocation+show+"/"+show+" - "+season+"x"+episode+" - "+eptitle+"."+container):
		try:
			epfile.retrieve(link,tvlocation+show+"/"+show+" - "+season+"x"+episode+" - "+eptitle+"."+container)
		except:
			print "Something went wrong downloading this episode... Deleting and retrying on next episode scan!"
			os.remove(tvlocation+show+"/"+show+" - "+season+"x"+episode+" - "+eptitle+"."+container)
	else:
		print "File already exists. Skipping episode."

def mvDownloader(moviefull,container,link):
	mvfile=urllib.URLopener()
	moviefull = re.sub(r'[\\/:"*?<>|"]+',"",moviefull)
	if not os.path.exists(movielocation+moviefull):
		os.makedirs(movielocation+moviefull)

	print "Downloading "+ moviefull + "..."

	if not os.path.isfile(movielocation+moviefull+"/"+moviefull+"."+container):
		try:
			mvfile.retrieve(link,movielocation+moviefull+"/"+moviefull+"."+container)
		except:
			print "Something went wrong downloading this movie... Deleting and retrying on next movie scan!"
			os.remove(movielocation+moviefull+"/"+moviefull+"."+container)			
	else:
		print "File already exists. Skipping movie."

def photoDownloader(albumname,picturename,link,container):
	photofile=urllib.URLopener()
	albumname = re.sub(r'[\\/:"*?<>|"]+',"",albumname)
	picturename = re.sub(r'[\\/:"*?<>|"]+',"",picturename)

	if not os.path.exists(picturelocation+albumname):
		os.makedirs(picturelocation+albumname)

	print "Downloading Album: "+ albumname + " Picture: " +picturename +" ..."

	if not os.path.isfile(picturelocation+albumname+"/"+picturename+"."+container):
		try:
			photofile.retrieve(link,picturelocation+albumname+"/"+picturename+"."+container)
		except:
			print "Something went wrong downloading this picture... Deleting and retrying on next picture scan!"
			os.remove(picturelocation+albumname+"/"+picturename+"."+container)			
	else:
		print "File already exists. Skipping picture."


def songDownloader(artist,cd,song,link,container):
	musicfile=urllib.URLopener()
	artist = re.sub(r'[\\/:"*?<>|"]+',"",artist)
	cd = re.sub(r'[\\/:"*?<>|"]+',"",cd)
	song = re.sub(r'[\\/:"*?<>|"]+',"",song)


	if not os.path.exists(musiclocation+artist):
		os.makedirs(musiclocation+artist)
	if not os.path.exists(musiclocation+artist+"/"+cd):
		os.makedirs(musiclocation+artist+"/"+cd)
	print "Downloading CD: "+ cd + " Song: "+song+  "..."

	if not os.path.isfile(musiclocation+artist+"/"+cd+"/"+song+"."+container):
		try:
			musicfile.retrieve(link,musiclocation+artist+"/"+cd+"/"+song+"."+container)
		except:
			print "Something went wrong downloading this song... Deleting and retrying on next music scan!"
			os.remove(musiclocation+artist+"/"+cd+"/"+song+"."+container)			
	else:
		print "Song already exists. Skipping song."

def tvShowSearch():
	tvopen = open(tvfile,"r")
	tvread = tvopen.read()
	tvlist= tvread.split("\n")
	tvopen.close()
	print str(len(tvlist)-1) + " TV Shows Found in Your Wanted List..."
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
		tvtitle = re.sub(r'[^\x00-\x7F]+',' ', tvtitle)
		tvtitle = re.sub(r'\&','and', tvtitle)
		if (tvtitle in tvlist) or (tvsync =="enable"):
			print tvtitle + " Found in Wanted List"
			if myplexstatus=="enable":
				seasonhttp=url+tvkey+"?X-Plex-Token="+plextoken
			else:
				seasonhttp=url+tvkey
			seasonweb = urllib.urlopen(seasonhttp)
			xmlseason = minidom.parse(seasonweb)
			seasonlist = xmlseason.getElementsByTagName('Directory')
			totalseasons =  len(seasonlist)
			latestseason = seasonlist[totalseasons-1].attributes['index'].value

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
							episoderatingkey = episode.attributes['ratingKey'].value
							try:
								#checks to see if episode has been viewed node is available
								tvviewcount = episode.attributes['lastViewedAt'].value
							except:
								#if fails to find lastViewedAt will notify script that tv is unwatched 
								tvviewcount = "unwatched"
							#checks if user wants unwatched only
							if tvunwatched=="enable":
								if tvviewcount=="unwatched":
									print "Episode is unwatched..."
								else:
									print "Episode is watched... skipping!"
									continue
							partindex = episode.getElementsByTagName('Part')
							for partitem in partindex:
								downloadkey = partitem.attributes['key'].value
								downloadcontainer = partitem.attributes['container'].value
							print tvtitle + " Season "+ seasonindex + " Episode " + episodeindex
							if myplexstatus=="enable":
								eplink=url+downloadkey+"?X-Plex-Token="+plextoken
							else:
								eplink=url+downloadkey
							if tvtranscode=="enable":
								tvTranscoder(tvtitle,seasonindex,episodeindex,downloadcontainer,eplink,episodetitle,episoderatingkey)
							else:							
								epDownloader(tvtitle,seasonindex,episodeindex,downloadcontainer,eplink,episodetitle)
					
					elif (tvtype=="episode"):
						seasonkey= season.attributes['key'].value
						seasonindex= season.attributes['index'].value
						if myplexstatus=="enable":
							episodehttp=url+seasonkey+"?X-Plex-Token="+plextoken
						else:
							episodehttp=url+seasonkey
						episodeweb=urllib.urlopen(episodehttp)
						xmlepisode=minidom.parse(episodeweb)
						episodelist=xmlepisode.getElementsByTagName('Video')
						totalepisodes= len(episodelist)
						latestepisode = totalepisodes
						for episode in episodelist:
							episodekey = episode.attributes['key'].value
							episodeindex = episode.attributes['index'].value
							episodetitle = episode.attributes['title'].value
							episoderatingkey = episode.attributes['ratingKey'].value

							try:
								#checks to see if episode has been viewed node is available
								tvviewcount = episode.attributes['lastViewedAt'].value
							except:
								#if fails to find lastViewedAt will notify script that tv is unwatched 
								tvviewcount = "unwatched"
							#checks if user wants unwatched only
							if tvunwatched=="enable":
								if tvviewcount=="unwatched":
									print "Episode is unwatched..."
								else:
									print "Episode is watched... skipping!"
									continue
							partindex = episode.getElementsByTagName('Part')
							for partitem in partindex:
								downloadkey = partitem.attributes['key'].value
								downloadcontainer = partitem.attributes['container'].value
							print tvtitle + " Season "+ seasonindex + " Episode " + episodeindex
							if myplexstatus=="enable":
								eplink=url+downloadkey+"?X-Plex-Token="+plextoken
							else:
								eplink=url+downloadkey
							if (episodeindex==str(latestepisode)) and (seasontitle=="Season "+str(latestseason)):
								if tvtranscode=="enable":
									tvTranscoder(tvtitle,seasonindex,episodeindex,downloadcontainer,eplink,episodetitle,episoderatingkey)
								else:							
									epDownloader(tvtitle,seasonindex,episodeindex,downloadcontainer,eplink,episodetitle)							
							elif (tvdelete=="enable"):
								if os.path.isfile(tvlocation+tvtitle+"/"+tvtitle+" - "+seasonindex+"x"+episodeindex+" - "+episodetitle+"."+downloadcontainer):
									try:
										print "Deleting old episode: Season "+str(seasonindex)+" Episode "+str(episodeindex)
										os.remove(tvlocation+tvtitle+"/"+tvtitle+" - "+seasonindex+"x"+episodeindex+" - "+episodetitle+"."+downloadcontainer)
									except:
										print "Could not delete old episode. Will try again on the next scan."
								else:
									print "Not the latest episode and no old file found so ignoring."
							else:
								print "Not the latest episode. Ignoring!"

					elif (tvtype=="recent"):
						if (seasontitle=="Season "+str(latestseason)):
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
								episoderatingkey = episode.attributes['ratingKey'].value

								try:
									#checks to see if episode has been viewed node is available
									tvviewcount = episode.attributes['lastViewedAt'].value
								except:
									#if fails to find lastViewedAt will notify script that tv is unwatched 
									tvviewcount = "unwatched"
								#checks if user wants unwatched only
								if tvunwatched=="enable":
									if tvviewcount=="unwatched":
										print "Episode is unwatched..."
									else:
										print "Episode is watched... skipping!"
										continue
								partindex = episode.getElementsByTagName('Part')
								for partitem in partindex:
									downloadkey = partitem.attributes['key'].value
									downloadcontainer = partitem.attributes['container'].value
								print tvtitle + " Season "+ seasonindex + " Episode " + episodeindex
								if myplexstatus=="enable":
									eplink=url+downloadkey+"?X-Plex-Token="+plextoken
								else:
									eplink=url+downloadkey	
								if tvtranscode=="enable":
									tvTranscoder(tvtitle,seasonindex,episodeindex,downloadcontainer,eplink,episodetitle,episoderatingkey)
								else:							
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
	print str(len(movielist)-1) + " Movies Found in Your Wanted List..."

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
		movietitle = re.sub(r'[^\x00-\x7F]+',' ', movietitle)
		movietitle = re.sub(r'\&','and', movietitle)
		moviedata = item.attributes['key'].value
		movieratingkey = item.attributes['ratingKey'].value
		try:
			movieyear = item.attributes['year'].value
		except:
			movieyear="Unknown"
		try:
			#checks to see if view count node is available
			movieviewcount = item.attributes['viewCount'].value
		except:
			#if fails to find viewCount will notify script that it can continue 
			movieviewcount = "unwatched"
		#checks if user wants unwatched only
		if movieunwatched=="enable":
			if movieviewcount=="unwatched":
				print movietitle + " ("+movieyear+") is unwatched..."
			else:
				print movietitle + " ("+movieyear+") is watched... skipping!"
				continue

		moviename = movietitle + " ("+movieyear+")"
		if (moviename in movielist) or (moviesync=="enable"):
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
			if movietranscode=="enable":
				mvTranscoder(moviename,moviecontainer,movieurl,movieratingkey)
			else:
				mvDownloader(moviename,moviecontainer,movieurl)
		else:
			print moviename + " Not Found in Wanted List."


def photoSearch():
	pictureopen = open(picturefile,"r")
	pictureread = pictureopen.read()
	picturelist= pictureread.split("\n")
	pictureopen.close()
	print str(len(picturelist)-1) + " Albums Found in Your Wanted List..."

	if myplexstatus=="enable":
		pichttp=url+"/library/sections/"+pictureid+"/all"+"?X-Plex-Token="+plextoken
	else:
		pichttp=url+"/library/sections/"+pictureid+"/all"
	website = urllib.urlopen(pichttp)
	xmldoc = minidom.parse(website)
	itemlist = xmldoc.getElementsByTagName('Directory') 
	print str(len(itemlist)) + " Total Albums Found"
	for item in itemlist:
		albumtitle = item.attributes['title'].value
		albumtitle = re.sub(r'[^\x00-\x7F]+',' ', albumtitle)
		albumtitle = re.sub(r'\&','and', albumtitle)
		albumkey = item.attributes['key'].value
		#checks if album is in your wanted list or if full sync is enabled
		if (albumtitle in picturelist) or (picturesync=="enable") :
			if myplexstatus=="enable":
				albumhttp=url+albumkey+"?X-Plex-Token="+plextoken
			else:
				albumhttp=url+albumkey
			albumweb=urllib.urlopen(albumhttp)
			xmlalbum=minidom.parse(albumweb)
			picturesinalbum=xmlalbum.getElementsByTagName('Photo')
			for pics in picturesinalbum:

				pictitle= pics.attributes['title'].value
				partalbum=pics.getElementsByTagName('Part')

				piccontainer = partalbum[0].attributes['container'].value
				pickey = partalbum[0].attributes['key'].value

				if myplexstatus=="enable":
					piclink=url+pickey+"?X-Plex-Token="+plextoken
				else:
					piclink=url+pickey
				print pictitle + albumtitle
				photoDownloader(albumtitle,pictitle,piclink,piccontainer)
				
		else:
			print albumtitle + " Album Not Found in Wanted List."



def musicSearch():
	musicopen = open(musicfile,"r")
	musicread = musicopen.read()
	musiclist= musicread.split("\n")
	musicopen.close()
	print str(len(musiclist)-1) + " Artists Found in Your Wanted List..."
	if myplexstatus=="enable":
		musichttp=url+"/library/sections/"+musicid+"/all"+"?X-Plex-Token="+plextoken
	else:
		musichttp=url+"/library/sections/"+musicid+"/all"
	website = urllib.urlopen(musichttp)
	xmldoc = minidom.parse(website)
	#Get list of artists
	itemlist = xmldoc.getElementsByTagName('Directory') 
	print str(len(itemlist)) + " Total Artists Found"
	for item in itemlist:
		musictitle = item.attributes['title'].value
		musictitle = re.sub(r'[^\x00-\x7F]+',' ', musictitle)
		musictitle = re.sub(r'\&','and', musictitle)
		musickey = item.attributes['key'].value
		if (musictitle in musiclist) or (musicsync=="enable"):
			if myplexstatus=="enable":
				cdhttp=url+musickey+"?X-Plex-Token="+plextoken
			else:
				cdhttp=url+musickey
			cdweb=urllib.urlopen(cdhttp)
			xmlcd=minidom.parse(cdweb)
			#get List of CDs
			cdlist=xmlcd.getElementsByTagName('Directory')	
			for cd in cdlist:
				cdtitle = cd.attributes['title'].value
				if (cdtitle != "All tracks"):
					cdkey = cd.attributes['key'].value				
					if myplexstatus=="enable":
						songhttp=url+cdkey+"?X-Plex-Token="+plextoken
					else:
						songhttp=url+cdkey
					songweb=urllib.urlopen(songhttp)
					xmlsong=minidom.parse(songweb)
					#Get List of Songs 
					songlist=xmlsong.getElementsByTagName('Track')	
					for song in songlist:
						songtitle = song.attributes['title'].value
						songrating = song.attributes['ratingKey'].value
						if songtitle=="":
							songtitle = songrating
						partindex = song.getElementsByTagName('Part')						
				
						songfile = partindex[0].attributes['key'].value
						songcontainer = partindex[0].attributes['container'].value

						if myplexstatus=="enable":
							songlink=url+songfile+"?X-Plex-Token="+plextoken
						else:
							songlink=url+songfile
						songDownloader(musictitle,cdtitle,songtitle,songlink,songcontainer)
				else:
					print "Skipping all leaves."
		else:
			print musictitle + " Not in Wanted List"


while True:
	try:
		if myplexstatus=="enable":
			plextoken = myPlexSignin(myplexusername,myplexpassword)
		if myplexstatus=="enable" and plextoken=="":
			print "Failed to login to myPlex. Please disable myPlex or enter your correct login."
			exit()
		if tvactive=="enable":
			tvShowSearch()
		if movieactive=="enable":
			movieSearch()		
		if pictureactive=="enable":
			photoSearch()
		if musicactive=="enable":
			musicSearch()

		print "Plex Download completed at "+ strftime("%Y-%m-%d %H:%M:%S")
		print "Sleeping "+str(sleepTime)+" Seconds..."
		time.sleep(sleepTime)
	except Exception,e: 
		print "Something went wrong: " + str(e)
		print "Plex Download failed at "+ strftime("%Y-%m-%d %H:%M:%S")
		print "Retrying in "+str(sleepTime)+" Seconds..."
		time.sleep(sleepTime)
