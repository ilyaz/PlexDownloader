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
from myplex import myPlexSignin

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

moviescrapetype = parser.get('scrape', 'moviesearch')
moviescrapelimit = int(parser.get('scrape', 'movielimit'))
tvscrapetype = parser.get('scrape', 'tvsearch')
tvscrapelimit = int(parser.get('scrape', 'tvlimit'))
scrapetimer = int(parser.get('scrape', 'timer'))


plexsession=str(uuid.uuid4())
socket.setdefaulttimeout(180)

plextoken=""

print "PlexScraper - v0.01"

#Itemfile is list of shows to include/exclude.  Exclude by adding a "!" at beginning of show name.
#Any blank line or line beginning with a hash mark are ignored.
#Mirror this with same routine in plexdl.py until a shared codebase is used
def ReadItemFile(itemfile):
    list = []
    try:
        fp = open(itemfile,"r")
        list = fp.read().split("\n")
        fp.close()
    except Exception as e:
        pass
    wantedlist = []
    skiplist = []
    if list:
        for l in list:
            l = l.strip()
            if l.startswith('!'):
                skiplist.append(l[1:])
            elif l.startswith('#'):  #allow a commment
                pass
            elif l:  #skip blank lines
                wantedlist.append(l)
    return (wantedlist,skiplist)

#Writes list to itemfile. Dedupes.
def WriteItemFile(itemfile,itemlist,skiplist):
    itemlist = list(set(itemlist))
    skiplist = list(set(skiplist))
    fp = open(itemfile,"w+")
    for item in itemlist:
        if item:
            w = fp.write(item+"\n")
    for item in skiplist:
        if item:
            w = fp.write("!"+item+"\n")
    fp.close()


def tvShowScraper(searchtype):
    x=0
    tvlist, skiplist = ReadItemFile(tvfile)
    print str(len(tvlist)) + " TV Shows Found in Your Wanted List..."
    if myplexstatus=="enable":
        tvhttp=url+"/library/sections/"+tvshowid+"/"+searchtype+"?X-Plex-Token="+plextoken
    else:
        tvhttp=url+"/library/sections/"+tvshowid+"/"+searchtype
    website = urllib.urlopen(tvhttp)
    xmldoc = minidom.parse(website)
    itemlist = xmldoc.getElementsByTagName('Directory')
    print str(len(itemlist)) + " Total TV Shows Found"
    for item in itemlist:
        tvkey = item.attributes['key'].value
        tvtitle = item.attributes['title'].value
        #tvtitle = re.sub(r'[^\x00-\x7F]+',' ', tvtitle)
        tvtitle = re.sub(r'\&','and', tvtitle)
        if (x <= tvscrapelimit):
            tvlist.append(tvtitle)
        x=x+1
    WriteItemFile(tvfile,tvlist,skiplist)



def movieScraper(searchtype):
    x=0
    movielist, skiplist = ReadItemFile(moviefile)
    print str(len(movielist)) + " Movies Found in Your Wanted List..."

    if myplexstatus=="enable":
        moviehttp=url+"/library/sections/"+movieid+"/"+searchtype+"?X-Plex-Token="+plextoken
    else:
        moviehttp=url+"/library/sections/"+movieid+"/"+searchtype
    website = urllib.urlopen(moviehttp)
    xmldoc = minidom.parse(website)
    itemlist = xmldoc.getElementsByTagName('Video')
    print str(len(itemlist)) + " Total Movies Found"
    for item in itemlist:
        movietitle = item.attributes['title'].value
        #movietitle = re.sub(r'[^\x00-\x7F]+',' ', movietitle)
        movietitle = re.sub(r'\&','and', movietitle)
        moviedata = item.attributes['key'].value
        movieratingkey = item.attributes['ratingKey'].value
        try:
            movieyear = item.attributes['year'].value
        except:
            movieyear="Unknown"
        moviename = movietitle + " ("+movieyear+")"
        if (x <= moviescrapelimit):
            movielist.append(moviename)
        x=x+1
    WriteItemFile(moviefile,movielist,skiplist)

# #todo: needs to be re-written per tv/movies functions
# def photoScraper(searchtype):
#     pictureopen = open(picturefile,"r")
#     pictureread = pictureopen.read()
#     picturelist= pictureread.split("\n")
#     pictureopen.close()
#     print str(len(picturelist)-1) + " Albums Found in Your Wanted List..."
#
#     if myplexstatus=="enable":
#         pichttp=url+"/library/sections/"+pictureid+"/"+searchtype+"?X-Plex-Token="+plextoken
#     else:
#         pichttp=url+"/library/sections/"+pictureid+"/"+searchtype
#     website = urllib.urlopen(pichttp)
#     xmldoc = minidom.parse(website)
#     itemlist = xmldoc.getElementsByTagName('Directory')
#     print str(len(itemlist)) + " Total Albums Found"
#     for item in itemlist:
#         albumtitle = item.attributes['title'].value
#         #albumtitle = re.sub(r'[^\x00-\x7F]+',' ', albumtitle)
#         albumtitle = re.sub(r'\&','and', albumtitle)
#         albumkey = item.attributes['key'].value

# #todo: needs to be re-written per tv/movies functions
# def musicScraper(searchtype):
#     musicopen = open(musicfile,"r")
#     musicread = musicopen.read()
#     musiclist= musicread.split("\n")
#     musicopen.close()
#     print str(len(musiclist)-1) + " Artists Found in Your Wanted List..."
#     if myplexstatus=="enable":
#         musichttp=url+"/library/sections/"+musicid+"/"+searchtype+"?X-Plex-Token="+plextoken
#     else:
#         musichttp=url+"/library/sections/"+musicid+"/"+searchtype
#     website = urllib.urlopen(musichttp)
#     xmldoc = minidom.parse(website)
#     #Get list of artists
#     itemlist = xmldoc.getElementsByTagName('Directory')
#     print str(len(itemlist)) + " Total Artists Found"
#     for item in itemlist:
#         musictitle = item.attributes['title'].value
#         #musictitle = re.sub(r'[^\x00-\x7F]+',' ', musictitle)
#         musictitle = re.sub(r'\&','and', musictitle)
#         musickey = item.attributes['key'].value

if tvscrapetype=="disable" and moviescrapetype=="disable":
    print "Plex Scraper: No scrapers enabled in config.  Scraper process disabled."
else:
    while True:
        try:
            if myplexstatus=="enable":
                plextoken = myPlexSignin(myplexusername,myplexpassword)
            if myplexstatus=="enable" and plextoken=="":
                print "Plex Scraper: Failed to login to myPlex. Please disable myPlex or enter your correct login."
                exit()
            if tvactive=="enable" and tvscrapetype != "disable":
                tvShowScraper(tvscrapetype)
            if movieactive=="enable" and moviescrapetype != "disable":
                movieScraper(moviescrapetype)
            #if pictureactive=="enable":
            #	photoScraper('recentlyAdded')
            #if musicactive=="enable":
            #	musicScraper('recentlyAdded')

            print "Plex Scraper: completed at "+ strftime("%Y-%m-%d %H:%M:%S")
            print "Plex Scraper: Sleeping "+str(scrapetimer)+" Seconds..."
            time.sleep(scrapetimer)
        except Exception,e:
            print "Plex Scraper: Something went wrong: " + str(e)
            print "Plex Scraper: Failed at "+ strftime("%Y-%m-%d %H:%M:%S")
            print "Plex Scraper: Retrying in "+str(scrapetimer)+" Seconds..."
            time.sleep(scrapetimer)
