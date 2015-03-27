# -*- coding: utf-8 -*-
import web
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

movieid = parser.get('movies', 'plexid')
movielocation = parser.get('movies', 'movielocation')
moviefile = parser.get('movies', 'moviefile')
moviesync = parser.get('movies', 'fullsync')
movieactive = parser.get('movies', 'active')

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


socket.setdefaulttimeout(30)

urls = (
	'/', 'index',
	'/sync', 'sync',
	'/delete', 'delete'
)

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


movielib= []
moviewanted=[]
def movieSearch():
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
		moviename = re.sub(r'[^\x00-\x7F]+',' ', moviename)
		moviename = re.sub(r'\&','and', moviename)
		try:
			movieyear = item.attributes['year'].value
		except:
			movieyear="Unknown"
		movielib.append(moviename+" ("+movieyear+")")

musiclib = []
musicwanted = []
def musicSearch():
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
		artistname = re.sub(r'[^\x00-\x7F]+',' ', artistname)
		artistname = re.sub(r'\&','and', artistname)
		musiclib.append(artistname)

albumlib=[]
albumwanted=[]
def photoSearch():
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
		albumtitle = re.sub(r'[^\x00-\x7F]+',' ', albumtitle)
		albumtitle = re.sub(r'\&','and', albumtitle)		
		albumlib.append(albumtitle)

tvlib=[]
tvwanted=[]
def tvShowSearch():
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
		tvtitle = re.sub(r'[^\x00-\x7F]+',' ', tvtitle)
		tvtitle = re.sub(r'\&','and', tvtitle)
		tvlib.append(tvtitle)

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


class index:
	def __init__(self):
		self.render = web.template.render('templates')
 
	def GET(self):
		return self.render.index(movielib,moviewanted,tvlib,tvwanted,musiclib,musicwanted,albumlib,albumwanted,url)

	def POST(self):
		data = web.data()
		return data

class sync:
	def GET(self):
		data = web.input()
		contype = data['type']
		content = data['content']
		if contype=="tvshow":
			tvopen = open(tvfile,"a")
			tvread = tvopen.write(content+"\n")
			tvopen.close()
			tvShowSearch()
			raise web.seeother('/')
		elif contype=="movie":
			movieopen = open(moviefile,"a")
			movieread = movieopen.write(content+"\n")
			movieopen.close()
			movieSearch()
			raise web.seeother('/')
		elif contype=="music":
			musicopen = open(musicfile,"a")
			musicread = musicopen.write(content+"\n")
			musicopen.close()
			musicSearch()
			raise web.seeother('/')
		elif contype=="picture":
			pictureopen = open(picturefile,"a")
			pictureread = pictureopen.write(content+"\n")
			pictureopen.close()
			photoSearch()
			raise web.seeother('/')

class delete:
	def GET(self):
		data = web.input()
		contype = data['type']
		content = data['content']
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
			tvShowSearch()
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
			movieSearch()
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
			musicSearch()
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
			photoSearch()
			raise web.seeother('/')

if __name__ == "__main__":
	app = web.application(urls, globals())
	app.run()
