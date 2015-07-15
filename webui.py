# -*- coding: utf-8 -*-
import web
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
import shutil
from myplex import myPlexSignin
from lib import movieSearch,tvShowSearch,photoSearch,musicSearch

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
tvsync = parser.get('tvshows', 'fullsync')
tvactive = parser.get('tvshows', 'active')
tvdelete = parser.get('tvshows', 'autodelete')
tvunsync = parser.get('tvshows', 'deletefiles')


movieid = parser.get('movies', 'plexid')
movielocation = parser.get('movies', 'movielocation')
moviefile = parser.get('movies', 'moviefile')
moviesync = parser.get('movies', 'fullsync')
movieactive = parser.get('movies', 'active')
movieunsync = parser.get('movies', 'deletefiles')

musicid = parser.get('music', 'plexid')
musiclocation = parser.get('music', 'musiclocation')
musicfile = parser.get('music', 'musicfile')
musicsync = parser.get('music', 'fullsync')
musicactive = parser.get('music', 'active')
musicunsync = parser.get('music', 'deletefiles')


pictureid = parser.get('pictures', 'plexid')
picturelocation = parser.get('pictures', 'picturelocation')
picturefile = parser.get('pictures', 'picturefile')
picturesync = parser.get('pictures', 'fullsync')
pictureactive = parser.get('pictures', 'active')
pictureunsync = parser.get('pictures', 'deletefiles')


socket.setdefaulttimeout(30)

urls = (
	'/', 'index',
	'/sync', 'sync',
	'/delete', 'delete',
        '/force', 'force'
)


movielib= []
moviewanted=[]
def movieSearchWeb():
	movielib[:]=[]
	moviewanted[:]=[]
	movieopen = open(moviefile,"r")
	movieread = movieopen.read()
	movielist= movieread.split("\n")
	moviewanted.extend(movielist)
	movieopen.close()
	if myplexstatus=="enable":
		moviehttp=url+"/library/sections/"+movieid+"/all"+"?X-Plex-Token="+plextoken
	else:
		moviehttp=url+"/library/sections/"+movieid+"/all"
	website = urllib.urlopen(moviehttp)
	xmldoc = minidom.parse(website)
	movielibrary = xmldoc.getElementsByTagName('Video')

	for item in movielibrary:
		moviename= item.attributes['title'].value
		#moviename = re.sub(r'[^\x00-\x7F]+',' ', moviename)
		moviename = re.sub(r'\&','and', moviename)
		try:
			movieyear = item.attributes['year'].value
		except:
			movieyear="Unknown"
		movielib.append(moviename+" ("+movieyear+")")

musiclib = []
musicwanted = []
def musicSearchWeb():
	musiclib[:]=[]
	musicwanted[:]=[]
	musicopen = open(musicfile,"r")
	musicread = musicopen.read()
	musiclist= musicread.split("\n")
	musicwanted.extend(musiclist)
	musicopen.close()
	if myplexstatus=="enable":
		musichttp=url+"/library/sections/"+musicid+"/all"+"?X-Plex-Token="+plextoken
	else:
		musichttp=url+"/library/sections/"+musicid+"/all"
	website = urllib.urlopen(musichttp)
	xmldoc = minidom.parse(website)
	#Get list of artists
	itemlist = xmldoc.getElementsByTagName('Directory')
	for item in itemlist:
		artistname= item.attributes['title'].value
		#artistname = re.sub(r'[^\x00-\x7F]+',' ', artistname)
		artistname = re.sub(r'\&','and', artistname)
		musiclib.append(artistname)

albumlib=[]
albumwanted=[]
def photoSearchWeb():
	albumlib[:]=[]
	albumwanted[:]=[]
	pictureopen = open(picturefile,"r")
	pictureread = pictureopen.read()
	picturelist= pictureread.split("\n")
	albumwanted.extend(picturelist)
	pictureopen.close()

	if myplexstatus=="enable":
		pichttp=url+"/library/sections/"+pictureid+"/all"+"?X-Plex-Token="+plextoken
	else:
		pichttp=url+"/library/sections/"+pictureid+"/all"
	website = urllib.urlopen(pichttp)
	xmldoc = minidom.parse(website)
	itemlist = xmldoc.getElementsByTagName('Directory')
	for item in itemlist:
		albumtitle = item.attributes['title'].value
		#albumtitle = re.sub(r'[^\x00-\x7F]+',' ', albumtitle)
		albumtitle = re.sub(r'\&','and', albumtitle)
		albumlib.append(albumtitle)

tvlib=[]
tvwanted=[]
def tvShowSearchWeb():
	tvlib[:]=[]
	tvwanted[:]=[]
	tvopen = open(tvfile,"r")
	tvread = tvopen.read()
	tvlist= tvread.split("\n")
	tvwanted.extend(tvlist)
	tvopen.close()
	if myplexstatus=="enable":
		tvhttp=url+"/library/sections/"+tvshowid+"/all"+"?X-Plex-Token="+plextoken
	else:
		tvhttp=url+"/library/sections/"+tvshowid+"/all"

	website = urllib.urlopen(tvhttp)
	xmldoc = minidom.parse(website)
	itemlist = xmldoc.getElementsByTagName('Directory')
	for item in itemlist:
		tvtitle = item.attributes['title'].value
		#tvtitle = re.sub(r'[^\x00-\x7F]+',' ', tvtitle)
		tvtitle = re.sub(r'\&','and', tvtitle)
		tvlib.append(tvtitle)

if myplexstatus=="enable":
	plextoken = myPlexSignin(myplexusername,myplexpassword)
if myplexstatus=="enable" and plextoken=="":
	print "Failed to login to myPlex. Please disable myPlex or enter your correct login."
	exit()
if tvactive=="enable":
	tvShowSearchWeb()
if movieactive=="enable":
	movieSearchWeb()
if pictureactive=="enable":
	photoSearchWeb()
if musicactive=="enable":
	musicSearchWeb()


class index:
	def __init__(self):
		self.render = web.template.render('templates')

	def GET(self):
		return self.render.index(movielib,moviewanted,tvlib,tvwanted,musiclib,musicwanted,albumlib,albumwanted,url)

	def POST(self):
		data = web.data()
		return data
class force:
	def GET(self):
		data = web.input()
		contype = data['type']
		if contype=="tvshow":
                        print "Force Searching TV Shows..."
			tvShowSearch()
			raise web.seeother('/')
		elif contype=="movie":
                        print "Force Searching Movies..."
			movieSearch()
			raise web.seeother('/')
		elif contype=="music":
                        print "Force Searching Music..."
			musicSearch()
			raise web.seeother('/')
		elif contype=="picture":
                        print "Force Searching Pictures..."
			photoSearch()
			raise web.seeother('/')

class sync:
	def GET(self):
		data = web.input()
		contype = data['type']
		content = data['content'].encode('utf8')
		if contype=="tvshow":
			tvopen = open(tvfile,"a")
			tvread = tvopen.write(content+"\n")
			tvopen.close()
			tvShowSearchWeb()
			raise web.seeother('/')
		elif contype=="movie":
			movieopen = open(moviefile,"a")
			movieread = movieopen.write(content+"\n")
			movieopen.close()
			movieSearchWeb()
			raise web.seeother('/')
		elif contype=="music":
			musicopen = open(musicfile,"a")
			musicread = musicopen.write(content+"\n")
			musicopen.close()
			musicSearchWeb()
			raise web.seeother('/')
		elif contype=="picture":
			pictureopen = open(picturefile,"a")
			pictureread = pictureopen.write(content+"\n")
			pictureopen.close()
			photoSearchWeb()
			raise web.seeother('/')

class delete:
	def GET(self):
		data = web.input()
		contype = data['type']
		content = data['content'].encode('utf8')
		if contype=="tvshow":
			tvopen = open(tvfile,"r")
			tvread = tvopen.read()
			tvlist= tvread.split("\n")
			if content in tvlist:
				tvlist.remove(content)
			while '' in tvlist:
				tvlist.remove('')
			tvopen.close()
			tvopen = open(tvfile,"w+")
			for item in tvlist:
				tvwrite = tvopen.write(item+"\n")
			tvopen.close()
			if tvunsync == "enable":
                            try:
                                shutil.rmtree(tvlocation + content)
                                print "Successfully deleted " + str(content)+ " from filesystem."
                            except:
                                print "Unable to delete tv show from filesystem. Check Permissions."
                        elif tvunsync == "disable":
                            print "Successfully removed from sync queue. Not deleting from filesystem due to settings."
			tvShowSearchWeb()
			raise web.seeother('/')
		elif contype=="movie":
			movieopen = open(moviefile,"r")
			movieread = movieopen.read()
			movielist= movieread.split("\n")
			if content in movielist:
				movielist.remove(content)
			while '' in movielist:
				movielist.remove('')
			movieopen.close()
			movieopen = open(moviefile,"w+")
			for item in movielist:
				moviewrite = movieopen.write(item+"\n")
			movieopen.close()
			if movieunsync == "enable":
                            try:
                                shutil.rmtree(movielocation + content)
                                print "Successfully deleted " + str(content)+ " from filesystem."
                            except:
                                print "Unable to delete movie from filesystem. Check Permissions."
                        elif movieunsync == "disable":
                            print "Successfully removed from sync queue. Not deleting from filesystem due to settings."
			movieSearchWeb()
			raise web.seeother('/')
		elif contype=="music":
			musicopen = open(musicfile,"r")
			musicread = musicopen.read()
			musiclist= musicread.split("\n")
			if content in musiclist:
				musiclist.remove(content)
			while '' in musiclist:
				musiclist.remove('')
			musicopen.close()
			musicopen = open(musicfile,"w+")
			for item in musiclist:
				musicwrite = musicopen.write(item+"\n")
			musicopen.close()
			if musicunsync == "enable":
                            try:
                                shutil.rmtree(musiclocation + content)
                                print "Successfully deleted " + str(content)+ " from filesystem."
                            except:
                                print "Unable to delete music from filesystem. Check Permissions."
                        elif musicunsync == "disable":
                            print "Successfully removed from sync queue. Not deleting from filesystem due to settings."
			musicSearchWeb()
			raise web.seeother('/')
		elif contype=="picture":
			pictureopen = open(picturefile,"r")
			pictureread = pictureopen.read()
			picturelist= pictureread.split("\n")
			if content in picturelist:
				picturelist.remove(content)
			while '' in picturelist:
				picturelist.remove('')
			pictureopen.close()
			pictureopen = open(picturefile,"w+")
			for item in picturelist:
				picturewrite = pictureopen.write(item+"\n")
			pictureopen.close()
			if pictureunsync == "enable":
                            try:
                                shutil.rmtree(picturelocation + content)
                                print "Successfully deleted " + str(content)+ " from filesystem."
                            except:
                                print "Unable to delete pictures from filesystem. Check Permissions."
                        elif pictureunsync == "disable":
                            print "Successfully removed from sync queue. Not deleting from filesystem due to settings."
			photoSearchWeb()
			raise web.seeother('/')

if __name__ == "__main__":
	app = web.application(urls, globals())
	app.run()
