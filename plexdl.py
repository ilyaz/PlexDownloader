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
#from urllib2 import Request, urlopen, quote
import urllib2
import base64
import uuid
import platform
from time import gmtime, strftime
import random
import string
from myplex import myPlexSignin
import traceback,sys

parser = SafeConfigParser()
parser.read('user.ini')

import subprocess

webstatus = parser.get('webui','status')
webport = parser.get('webui','port')
if webstatus=="enable":
    print "Starting PlexDownloader Web Manager..."
    subprocess.Popen(["python", "webui.py", webport])

print "Starting Plex Scraper..."
subprocess.Popen(["python", "scrape.py"])

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
tvstructure=parser.get('tvshows','folderstructure')

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
moviestructure = parser.get('movies','folderstructure')

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


mimetypes = { "video/avi":"avi", "video/mpeg":"mpeg", "video/mp4":"mp4", "video/x-matroska":"mkv" }
videoext = ['avi','mpeg','mpg','mp4','mkv']

#random_data = os.urandom(128)
#plexsession = hashlib.md5(random_data).hexdigest()[:16]
plexsession=str(uuid.uuid4())
socket.setdefaulttimeout(180)

debug_limitdld = False      #set to true during development to limit size of downloaded files
debug_outputxml = False     #output relevant XML when exceptions occur
debug_pretenddld = False     #set to true to fake downloading
debug_pretendremove = False   #set to true to fake removing files
verbose = 0

plextoken=""

print "PlexDownloader - v0.05"

def getSeasonAndEpisode(filename):
    #todo: Add in syntax below for multi-episode formats
    m = re.findall(r"(?ix)(?:[\s\.\-,_])(?:s)(\d{1,3})(?:e|x)(\d{1,3})", filename, re.I)   #s1e1,s1x1
    if not m:
        m = re.findall(r"(?ix)(?:[\s\.\-,_])(\d{1,3})(?:e|x)(\d{1,3})", filename, re.I)  #1e1,1x1
    return (int(m[0][0]),int(m[0][1]))  #returns integer version of just the first match in the filename

#"server" structure is "tvlocation/show name/Season X/episodes"
#"default" structure is "tvlocation/show name/episodes"
def getTvFullFilename(show,season,episode,eptitle,container=None):
    if tvstructure == "server":
        #f = tvlocation+show+"/Season "+season+"/"+show+" - s"+season+"e"+episode+" - "+eptitle
        f = os.path.join(movielocation, part['foldername'], os.path.splitext(part['filename'])[0])
    else:
        #f = tvlocation+show+"/"+show+" - "+season+"x"+episode+" - "+eptitle
        f = os.path.join(tvlocation, show, show+" - s"+season+"e"+episode+" - "+eptitle)
    if container:
        f = f+"."+container
    return f

#"server" structure uses the foldername and filename of the Plex server"
#"default" structure is "tvlocation/show name/episodes"
def getTvFullFilenameByPart(show,season,episode,eptitle,part,container=None):
    if tvstructure == "server":
        #f = tvlocation+show+"/Season "+season+"/"+show+" - s"+season+"e"+episode+" - "+eptitle
        #OLD---f = os.path.join(movielocation, part['foldername'], os.path.splitext(part['filename'])[0])
        f = os.path.join(tvlocation, show, part['foldername'], os.path.splitext(part['filename'])[0])
    else:
        #f = tvlocation+show+"/"+show+" - "+season+"x"+episode+" - "+eptitle
        f = os.path.join(tvlocation, show, show+" - s"+season+"e"+episode+" - "+eptitle)
    if container:
        f = f+"."+container
    return f

#Path format of "movielocation/movie name (year)/videos"
#"server" structure uses the foldername and filename of the Plex server"
#"default" structure uses generated folder and filenames
def getMovieFullFilename(moviename,part,container=None):
    if moviestructure == "server":
        f = os.path.join(movielocation, part['foldername'], os.path.splitext(part['filename'])[0])
    else:
        f = os.path.join(movielocation, moviename, moviename)
    if container:
        f = f+"."+container
    return f

def isValidVideoFile(filename):
    try:
        ext = os.path.splitext(filename)[1].lower()[1:]
        if ext in videoext:
            return True
        return False
    except Exception as e:
        #print(traceback.format_exc())
        return False

#checks if a tv episode exists based on season/episode.  Handles both tvstructure choices
#returns full path to file if it exists, None if it does not
#Note that this specifically will locate a "show[*].pt1.mkv" file
#regardless of what specific part is passed
#Any valid video extension is considered found
#NOT USED RIGHT NOW.  ARCHIVED FOR USE LATER
# def tvEpisodeExistsFlex(show,season,episode):
#     dirs = []
#     season=int(season)
#     episode=int(episode)
#     if tvstructure == "server":
#         dirs.append(os.path.join(tvlocation, show, "Season "+str(season).zfill(1)))
#         dirs.append(os.path.join(tvlocation, show, "Season "+str(season).zfill(2)))
#         dirs.append(os.path.join(tvlocation, show, "Season "+str(season).zfill(3)))
#         if season == 0:
#             dirs.append(os.path.join(tvlocation, show, "Specials"))
#     else:
#         dirs.append(os.path.join(tvlocation,show))
#     #pattern = '(?ix)(?:[\s\.\-,_])(?:s)?(\d{1,3})(?:e|x)(\d{1,3})(?:-[ex](\d{1,3}))?(?:[\s\.\-,_])'
#     #also handle s1e01-e04 format
#     pattern = '(?ix)(?:s)?(\d{1,3})(?:e|x)(\d{1,3})(?:-[ex](\d{1,3}))?(?:[\s\.\-,_])'  #handle where it just starts with S01
#     r = re.compile(pattern)
#     for folder in dirs:
#         if os.path.isdir(folder):
#             for f in os.listdir(folder):
#                 result = r.search(f)
#                 if result and isValidVideoFile(f):
#                     if episode == int(result.groups()[1]):
#                         return os.path.join(folder,f)
#                     if result.groups()[2]: # process s1e01-e04 files
#                         #print result.groups()
#                         if episode >= int(result.groups()[1]) and episode <= int(result.groups()[2]):
#                             return os.path.join(folder,f)
#     return None

#checks if a tv episode exists based on season/episode.  Handles both tvstructure choices
#returns full path to file if it exists, None if it does not
#Note that this specifically will locate a "show[*].pt1.mkv" file
#regardless of what specific part is passed
#Any valid video extension is considered found
def tvEpisodeExists(show,season,episode,part):
    season=int(season)
    episode=int(episode)
    #in server mode be strict about what to match against. Must be exactly the same.
    if tvstructure == "server":
        filepath=getTvFullFilenameByPart(show,season,episode,"", part)
        folder=os.path.dirname(filepath)
        filename=os.path.basename(filepath)
        if os.path.isdir(folder):
            for f in os.listdir(folder):
                if f.startswith(filename):
                    if isValidVideoFile(f):
                        return os.path.join(folder,f)
                    else:
                        #print "Located " + f + " but is invalid extension"
                        pass
        return None
    #Be more flexible with searching for existing shows.
    dirs = []
    dirs.append(os.path.join(tvlocation,show))
    #also handle s1e01-e04 format
    pattern = '(?ix)(?:s)?(\d{1,3})(?:e|x)(\d{1,3})(?:-[ex](\d{1,3}))?(?:[\s\.\-,_])'  #handle where it just starts with S01
    r = re.compile(pattern)
    for folder in dirs:
        if os.path.isdir(folder):
            for f in os.listdir(folder):
                result = r.search(f)
                if result and isValidVideoFile(f):
                    if episode == int(result.groups()[1]):
                        return os.path.join(folder,f)
                    if result.groups()[2]: # process s1e01-e04 files
                        #print result.groups()
                        if episode >= int(result.groups()[1]) and episode <= int(result.groups()[2]):
                            return os.path.join(folder,f)
    return None

#checks if a movie exists.  Handles both moviestructure choices
#returns full path to file if it exists, None if it does not.
#Note that this specifically will locate a "movie (year).pt1.mkv" file
#regardless of what specific part is passed
#Any valid video extension is considered found movie
def movieExists(moviefoldername,part):
    filepath=getMovieFullFilename(moviefoldername,part)
    folder=os.path.dirname(filepath)
    filename=os.path.basename(filepath)
    if os.path.isdir(folder):
        for f in os.listdir(folder):
            if f.startswith(filename):
                if isValidVideoFile(f):
                    return os.path.join(folder,f)
                else:
                    #print "Located " + f + " but is invalid extension"
                    pass
    return None


def getDownloadURL(plexkey,quality,width,height,bitrate,session,token,partindex=0):
    clientuid = uuid.uuid4()
    clientid = clientuid.hex[0:16]
    link = (url+"/video/:/transcode/universal/start?path=http%3A%2F%2F127.0.0.1%3A32400"+plexkey+
            "&mediaIndex=0"+
            "&partIndex="+str(partindex)+
            "&protocol=http"+
            "&offset=0"+
            "&fastSeek=1"+
            "&directPlay=0"+
            "&directStream=1"+
            "&includeCodecs=1"+
            "&videoQuality="+quality+
            "&videoResolution="+width+"x"+height+
            "&maxVideoBitrate="+bitrate+
            "&subtitleSize=100"+
            "&audioBoost=100"+
            "&session="+session+
            "&X-Plex-Client-Profile-Extra=add-transcode-target-audio-codec(type%3DvideoProfile%26context%3Dstreaming%26protocol%3Dhls%26audioCodec%3Daac)"+  #restrict audiocodec to aac
            "&X-Plex-Client-Identifier="+clientid+
            "&X-Plex-Product=Plex Web"+
            "&X-Plex-Device=Plex Downloader"+
            "&X-Plex-Platform=Web"+
            "&X-Plex-Platform-Version=43.0"+
            "&X-Plex-Version=2.4.9"
            )
    if myplexstatus=="enable":
        link = link+"&X-Plex-Token="+token
    return link

def getDownloadURL2(metadata,quality,width,height,bitrate,session,token):
    clientuid = uuid.uuid4()
    clientid = clientuid.hex[0:16]
    link = (url+"/video/:/transcode/universal/start?path=http%3A%2F%2F127.0.0.1%3A32400%2Flibrary%2Fmetadata%2F"+metadata+
            "&mediaIndex=0"+
            "&partIndex=0"+
            "&protocol=http"+
            "&offset=0"+
            "&fastSeek=1"+
            "&directPlay=0"+
            "&directStream=1"+
            "&includeCodecs=1"+
            "&videoQuality="+quality+
            "&videoResolution="+width+"x"+height+
            "&maxVideoBitrate="+bitrate+
            "&subtitleSize=100"+
            "&audioBoost=100"+
            "&session="+session+
            "&X-Plex-Client-Profile-Extra=add-transcode-target-audio-codec(type%3DvideoProfile%26context%3Dstreaming%26protocol%3Dhls%26audioCodec%3Daac)"+  #restrict audiocodec to aac
            "&X-Plex-Client-Identifier="+clientid+
            "&X-Plex-Product=Plex Web"+
            "&X-Plex-Device=Plex Downloader"+
            "&X-Plex-Platform=Web"+
            "&X-Plex-Platform-Version=43.0"+
            "&X-Plex-Version=2.4.9"
            )
    if myplexstatus=="enable":
        link = link+"&X-Plex-Token="+token
    return link


def mvTranscoder(moviefull, container, link, moviemetadata):
    container = "mkv"
    plexproduct = "Plex-Downloader"
    plexdevice = "Plex-Downloader"
    plexsession = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(16))
    devicename = socket.gethostname()
    plexplatform = platform.system()
    clientplatform = platform.system()
    platformversion = platform.version()
    plexprovides = "controller"
    link = getDownloadURL2(moviemetadata, moviequality, moviewidth, movieheight, moviebitrate, plexsession, plextoken)
    print "Transcode URL: " + link

    mvfile = urllib.URLopener()
    moviefull = getFilesystemSafeName(moviefull)
    if not os.path.exists(movielocation + moviefull):
        os.makedirs(movielocation + moviefull)

    print "Downloading transcoded " + moviefull + "..."

    if not os.path.isfile(movielocation + moviefull + "/" + moviefull + "." + container):
        try:
            mvfile.retrieve(link, movielocation + moviefull + "/" + moviefull + "." + container)
        except Exception as e:
            print "Something went wrong transcoding this movie... Deleting and retrying on next movie scan!"
            os.remove(movielocation + moviefull + "/" + moviefull + "." + container)
    else:
        print "File already exists. Skipping movie transcode."

def mvTranscoder2(moviefoldername,plexkey,parts):
    plexsession = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(16))
    #plexsession = "z9fja0pznf40anzd"
    for counter, part in enumerate(parts):
        link = getDownloadURL(plexkey,moviequality,moviewidth, movieheight, moviebitrate,plexsession,plextoken,counter)
        #print "Transcode URL: "+link
        if len(parts) > 1:
            print "Downloading transcoded "+ moviefoldername +"... Part %d of %d" % (counter+1, len(parts))
        else:
            print "Downloading transcoded "+ moviefoldername+"..."
        if not downloadPart(link, getMovieFullFilename(moviefoldername,part),counter,len(parts),overwrite=False):
            print "Video not downloaded"


def tvTranscoder2(show,season,episode,eptitle,plexkey,parts):
    plexsession = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(16))
    #plexsession = "z9fja0pznf40anzd"
    for counter, part in enumerate(parts):
        link = getDownloadURL(plexkey,tvquality,tvwidth,tvheight,tvbitrate,plexsession,plextoken,counter)
        eptitle = getFilesystemSafeName(eptitle)
        if len(parts) > 1:
            print "Downloading transcoded "+ show + " Season "+season+" Episode "+episode+"... Part %d of %d" % (counter+1, len(parts))
        else:
            print "Downloading transcoded "+ show + " Season "+season+" Episode "+episode+"..."
        if not downloadPart(link, getTvFullFilenameByPart(show,season,episode,eptitle,part),counter,len(parts),overwrite=False):
            print "Video file not downloaded"


def tvTranscoderOld(show,season,episode,container,link,eptitle,tvmetadata):
    return
    container = "mkv"
    plexproduct = "Plex-Downloader"
    plexdevice = "Plex-Downloader"
    devicename = socket.gethostname()
    plexplatform = platform.system()
    clientplatform = platform.system()
    platformversion = platform.version()
    plexsession = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(16))
    plexsession = "z9fja0pznf40anzd"
    plexprovides = "controller"
    link = getDownloadURL2(tvmetadata,tvquality,tvwidth,tvheight,tvbitrate,plexsession,plextoken)
    print "Transcode URL: "+link
    epfile=urllib.URLopener()
    eptitle = getFilesystemSafeName(eptitle)
    filename=getTvFullFilename(show,season,episode,eptitle,container)
    if not os.path.exists(os.path.split(filename)[0]):
        os.makedirs(os.path.split(filename)[0])

    print "Downloading transcoded "+ show + " Season "+season+" Episode "+episode+"..."

    if not os.path.isfile(filename):
        try:
            epfile.retrieve(link,filename)
        except Exception as e:
            print "Something went wrong transcoding this episode... Deleting and retrying on next episode scan!"
            os.remove(filename)
    else:
        print "File already exists. Skipping episode transcode."

def epDownloader(show,season,episode,container,link,eptitle):
    epfile=urllib.URLopener()
    eptitle = getFilesystemSafeName(eptitle)
    filename=getTvFullFilename(show,season,episode,eptitle,container)
    if not os.path.exists(os.path.split(filename)[0]):
        os.makedirs(os.path.split(filename)[0])

    print "Downloading "+ show + " Season "+season+" Episode "+episode+"..."

    if not os.path.isfile(filename):
        try:
            epfile.retrieve(filename)
        except Exception as e:
            print "Something went wrong downloading this episode... Deleting and retrying on next episode scan!"
            os.remove(filename)
    else:
        print "File already exists. Skipping episode."

#Downloads all video parts passed in.  Will detect the type of video file and add the
#correct extension to file.  Handles multi-part video files.
#Will overwrite existing files if "overwrite==True"
#Returns True on download, False on no-download or failure
def downloadPart(link,filename,part=0,parts=1,overwrite=False):
    try:
        cleanup = False  #gracefully cleanup failed transcodes so we can try again
        if not os.path.exists(os.path.split(filename)[0]):
            os.makedirs(os.path.split(filename)[0])
        epfile = urllib.urlopen(link)
        mimetype = epfile.info().type
        #print mimetype
        container = mimetypes[mimetype]
        if not container:
            print "Warning: Unknown mimetype for file ({0}) Using MKV as default" % (mimetype)
            container = "mkv"  #use this as default
        if parts > 1:
            filename=filename+".pt"+str(part+1)
        filename=filename+"."+container
        if debug_pretenddld: return True
        if overwrite or (not os.path.isfile(filename)):
            with open(filename, "wb") as fp:
                cleanup = True
                while True:
                    chunk = epfile.read(1024*1024)  #1MB buffer
                    if not chunk: break
                    fp.write(chunk)
                    if debug_limitdld: break   #for development. limit to a single buffer size for output
            return True
        else:
            print "File already exists. Skipping transcode."
            return False
    except (KeyboardInterrupt, SystemExit):
        try:
            if cleanup: os.remove(filename)
        except:
            pass
        raise KeyboardInterrupt()
    except Exception as e:
        print "Something went wrong transcoding video... Deleting and retrying on next scan!"
        print "Something went wrong: " + str(e)
        print(traceback.format_exc())
        try:
            if cleanup: os.remove(filename)
        except:
            pass

    return False

def getMediaParts(node):
    try:
        partindex = node.getElementsByTagName('Part')
        parts = []
        for counter, partitem in enumerate(partindex):
            downloadkey = partitem.attributes['key'].value
            filepath = urllib.unquote(partitem.attributes['file'].value)
            #even on Linux, need to encode to cp1252 to handle extended characters
            filepath = filepath.encode("cp1252").decode("utf-8")
            filename = os.path.basename(filepath)
            foldername = os.path.dirname(os.path.realpath(filepath))
            foldername = os.path.basename(os.path.realpath(foldername))
            parts.append({"num":counter+1, "key":downloadkey, "filename":filename,"foldername":foldername})
        return parts
    except Exception as e:
        print(traceback.format_exc())
        return None

def getFilesystemSafeName(s):
    s = re.sub(r'[\\/:"*?<>|"]+',"",s)
    return s

def mvDownloader(moviefull,container,link,filename,foldername):
    mvfile=urllib.URLopener()
    moviefull = getFilesystemSafeName(moviefull)
    if moviestructure == "server":
        if not os.path.exists(movielocation+foldername):
            os.makedirs(movielocation+foldername)

        print "Downloading "+ moviefull + "..."

        if not os.path.isfile(movielocation+foldername+"/"+filename):
            try:
                mvfile.retrieve(link,movielocation+foldername+"/"+filename)
            except Exception as e:
                print "Something went wrong downloading this movie... Deleting and retrying on next movie scan!" + str(e)
                os.remove(movielocation+foldername+"/"+filename)
        else:
            print "File already exists. Skipping movie."
    else:
        if not os.path.exists(movielocation+moviefull):
            os.makedirs(movielocation+moviefull)

        print "Downloading "+ moviefull + "..."

        if not os.path.isfile(movielocation+moviefull+"/"+moviefull+"."+container):
            try:
                mvfile.retrieve(link,movielocation+moviefull+"/"+moviefull+"."+container)
            except Exception as e:
                print "Something went wrong downloading this movie... Deleting and retrying on next movie scan!"
                os.remove(movielocation+moviefull+"/"+moviefull+"."+container)
        else:
            print "File already exists. Skipping movie."

def photoDownloader(albumname,picturename,link,container):
    photofile=urllib.URLopener()
    albumname = getFilesystemSafeName(albumname)
    picturename = getFilesystemSafeName(picturename)

    if not os.path.exists(picturelocation+albumname):
        os.makedirs(picturelocation+albumname)

    print "Downloading Album: "+ albumname + " Picture: " +picturename +" ..."

    if not os.path.isfile(picturelocation+albumname+"/"+picturename+"."+container):
        try:
            photofile.retrieve(link,picturelocation+albumname+"/"+picturename+"."+container)
        except Exception as e:
            print "Something went wrong downloading this picture... Deleting and retrying on next picture scan!"
            os.remove(picturelocation+albumname+"/"+picturename+"."+container)
    else:
        print "File already exists. Skipping picture."


def songDownloader(artist,cd,song,link,container):
    musicfile=urllib.URLopener()
    artist = getFilesystemSafeName(artist)
    cd = getFilesystemSafeName(cd)
    song = getFilesystemSafeName(song)


    if not os.path.exists(musiclocation+artist):
        os.makedirs(musiclocation+artist)
    if not os.path.exists(musiclocation+artist+"/"+cd):
        os.makedirs(musiclocation+artist+"/"+cd)
    print "Downloading CD: "+ cd + " Song: "+song+  "..."

    if not os.path.isfile(musiclocation+artist+"/"+cd+"/"+song+"."+container):
        try:
            musicfile.retrieve(link,musiclocation+artist+"/"+cd+"/"+song+"."+container)
        except Exception as e:
            print "Something went wrong downloading this song... Deleting and retrying on next music scan!"
            os.remove(musiclocation+artist+"/"+cd+"/"+song+"."+container)
    else:
        print "Song already exists. Skipping song."

def constructUrl(key):
    http = str(url) + str(key)
    if myplexstatus=="enable":
        http +="?X-Plex-Token="+plextoken
    #print http
    return http

def tvShowSearch():
    tvopen = open(tvfile,"r")
    tvread = tvopen.read()
    tvlist= tvread.split("\n")
    tvopen.close()
    print str(len(tvlist)-1) + " TV Shows Found in Your Wanted List..."
    website = urllib.urlopen(constructUrl("/library/sections/"+tvshowid+"/all"))
    xmldoc = minidom.parse(website)
    itemlist = xmldoc.getElementsByTagName('Directory')
    print str(len(itemlist)) + " Total TV Shows Found"
    syncedItems = 0
    failedItems = 0
    removedItems = 0
    for item in itemlist:
        tvkey = item.attributes['key'].value
        tvtitle = item.attributes['title'].value
        tvtitle = re.sub(r'[^\x00-\x7F]+',' ', tvtitle)
        tvtitle = re.sub(r'\&','and', tvtitle)
        tvfoldername = getFilesystemSafeName(tvtitle)
        if (tvtitle in tvlist) or (tvsync =="enable"):
            print tvtitle + " Found in Wanted List"
            seasonweb = urllib.urlopen(constructUrl(tvkey))
            xmlseason = minidom.parse(seasonweb)
            seasonlist = xmlseason.getElementsByTagName('Directory')
            #construct list of episodes to sync
            episodelist = []
            if (tvtype=="all") or (tvtype=="episode"):    #download everything
                for season in seasonlist:
                    if season.hasAttribute('index'):   #skip "allSeasons"
                        episodeweb=urllib.urlopen(constructUrl(season.attributes['key'].value))
                        xmlepisode = minidom.parse(episodeweb)
                        for e in xmlepisode.getElementsByTagName('Video'):
                            e.setAttribute('seasonIndex', season.attributes['index'].value)
                            episodelist.append(e)
            elif (tvtype=="recent"): #download latest season
                episodeweb=urllib.urlopen(constructUrl(seasonlist[len(seasonlist)-1].attributes['key'].value))
                xmlepisode = minidom.parse(episodeweb)
                for e in xmlepisode.getElementsByTagName('Video'):
                    e.setAttribute('seasonIndex', seasonlist[len(seasonlist)-1].attributes['index'].value)
                    episodelist.append(e)
            for counter, episode in enumerate(episodelist):
                try:
                    episodekey = episode.attributes['key'].value
                    episodeindex = episode.attributes['index'].value
                    episodetitle = episode.attributes['title'].value
                    seasonindex = episode.attributes['seasonIndex'].value  #hack that we added in
                    #check if this already exists
                    try:
                        #checks to see if episode has been viewed node is available
                        tvviewcount = episode.attributes['lastViewedAt'].value
                    except Exception as e:
                        #if fails to find lastViewedAt will notify script that tv is unwatched
                        tvviewcount = "unwatched"
                    #checks if user wants unwatched only
                    if tvunwatched=="enable":
                        if tvviewcount=="unwatched":
                            if verbose: print "Episode is unwatched..."
                        else:
                            if verbose: print "Episode is watched... skipping!"
                            continue
                    parts = getMediaParts(episode)
                    if tvtype=="episode" and (counter != len(episodelist)-1):
                        if tvdelete=="enable":
                            #clean-up old episodes
                            #this logic isn't perfect.  It will not delete files that have been removed from the server.
                            fn = tvEpisodeExists(tvfoldername,seasonindex,episodeindex,parts[0])
                            if fn:
                                try:
                                    print "Deleting old episode: " + fn
                                    if not debug_pretendremove: os.remove(fn)
                                    removedItems += 1
                                except Exception as e:
                                    failedItems += 1
                                    print "Could not delete old episode. Will try again on the next scan."
                        continue
                    if tvEpisodeExists(tvfoldername,seasonindex,episodeindex,parts[0]):
                        if verbose: print tvtitle + " Season "+ seasonindex + " Episode " + episodeindex + " exists..."
                        continue
                    #print tvtitle + " Season "+ seasonindex + " Episode " + episodeindex
                    if tvtranscode=="enable":
                        tvTranscoder2(tvfoldername,seasonindex,episodeindex,episodetitle,episodekey,parts)
                    else:
                        #epDownloader(tvfoldername,seasonindex,episodeindex,downloadcontainer,eplink,episodetitle)
                        pass
                    syncedItems += 1
                except Exception as e:
                    failedItems += 1
                    print "Error syncing episode.  Skipping..."
                    print(traceback.format_exc())
                    if debug_outputxml: print episode.toprettyxml(encoding='utf-8')
        else:
            print tvtitle + " Not Found in Wanted List."
    if syncedItems > 0 or failedItems > 0 or removedItems > 0:
        print "TV synch complete: {0} downloaded, {1} removed, {2} errors" % (syncedItems, removedItems, failedItems)


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
    syncedItems = 0
    failedItems = 0
    for item in itemlist:
        movietitle = item.attributes['title'].value
        movietitle = re.sub(r'[^\x00-\x7F]+',' ', movietitle)
        movietitle = re.sub(r'\&','and', movietitle)
        moviekey = item.attributes['key'].value
        try:
            movieyear = item.attributes['year'].value
        except Exception as e:
            movieyear="Unknown"
        try:
            #checks to see if view count node is available
            movieviewcount = item.attributes['viewCount'].value
        except Exception as e:
            #if fails to find viewCount will notify script that it can continue
            movieviewcount = "unwatched"
        #checks if user wants unwatched only
        if movieunwatched=="enable":
            if movieviewcount=="unwatched":
                print movietitle + " ("+movieyear+") is unwatched..."
            else:
                if verbose: print movietitle + " ("+movieyear+") is watched... skipping!"
                continue
        moviename = movietitle + " ("+movieyear+")"
        if (moviename in movielist) or (moviesync=="enable"):
            try:
                moviefoldername = getFilesystemSafeName(moviename)
                parts = getMediaParts(item)
                existingfile = movieExists(moviefoldername,parts[0])
                if existingfile:
                    if verbose: print movietitle + " ("+movieyear+") exists... skipping!"
                    continue
                if movietranscode=="enable":
                    mvTranscoder2(moviefoldername,moviekey,parts)
                else:
                    #mvDownloader(moviefoldername,moviecontainer,movieurl,filename,foldername)
                    pass
                syncedItems += 1
            except Exception as e:
                failedItems += 1
                print "Error syncing " + moviename + ".  Skipping..."
                print(traceback.format_exc())
                if debug_outputxml: print item.toprettyxml(encoding='utf-8')
        else:
            if verbose: print moviename + " Not Found in Wanted List."
    if syncedItems > 0 or failedItems > 0:
        print "Movie synch complete: {0} downloaded  {1} errors" % (syncedItems, failedItems)

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
    except Exception as e:
        print "Something went wrong: " + str(e)
        print(traceback.format_exc())
        print "Plex Download failed at "+ strftime("%Y-%m-%d %H:%M:%S")
        print "Retrying in "+str(sleepTime)+" Seconds..."
        time.sleep(sleepTime)
