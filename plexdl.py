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

from __future__ import unicode_literals
from xml.dom import minidom
import urllib
import os
import time
from ConfigParser import SafeConfigParser
import re
import socket
#from urllib2 import Request, urlopen, quote
import urllib2
import uuid
from time import gmtime, strftime
import random
import string
from myplex import myPlexSignin
import traceback,sys,codecs

parser = SafeConfigParser()
parser.read('user.ini')

import subprocess

#redo stdout so unicode can be printed to the screen.  Otherwise would have to encode the output of every print message
#only necessary on Python2. Can be removed for Python3
if not sys.stdout.isatty():
    # set encoding when redirected
    if sys.stdout.encoding != 'UTF-8':
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
else:
    if sys.stdout.encoding != 'UTF-8':
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout)
if sys.stderr.encoding != 'UTF-8':
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr)

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

pictureid = parser.get('pictures', 'plexid')
picturelocation = parser.get('pictures', 'picturelocation')
picturefile = parser.get('pictures', 'picturefile')
picturesync = parser.get('pictures', 'fullsync')
pictureactive = parser.get('pictures', 'active')

mimetypes = {   #Keep these all lowercase!
    u'application/x-mpegurl':u'm3u8',
    u'application/vnd.apple.mpegurl':u'm3u8',
    u'application/octet-stream':u'm2ts',
    u'application/dash+xml':u'mpd',
    u'text/xml':u'xml',

    u'video/3gpp':u'3gp',
    u'video/avi':u'avi',
    u'video/mp2t':u'ts',
    u'video/mp4':u'mp4',
    u'video/mpeg':u'mpeg',
    u'video/ogg':u'ogv',
    u'video/quicktime':u'mov',
    u'video/x-flv':u'flv',
    u'video/x-matroska':u'mkv',
    u'video/x-msvideo':u'avi',
    u'video/x-ms-wmv':u'wmv',
    u'video/webm':u'webm',

    u'image/jpeg':	u'jpg',
    u'image/x-ms-bmp':u'bmp',
    u'image/gif':	u'gif',
    u'image/vnd.microsoft.icon':	u'ico',
    u'image/ief':	u'ief',
    u'image/x-portable-bitmap':	u'pbm',
    u'image/x-portable-graymap':	u'pgm',
    u'image/png':	u'png',
    u'image/x-portable-anymap':	u'pnm',
    u'image/x-portable-pixmap':	u'ppm',
    u'image/x-cmu-raster':	u'ras',
    u'image/x-rgb':	u'rgb',
    u'image/tiff':	u'tiff',
    u'image/x-xbitmap':	u'xbm',
    u'image/x-xpixmap':	u'xpm',
    u'image/x-xwindowdump':	u'xwd',
    u'image/jpg':	u'jpg',
    u'image/pict':	u'pic',

    u'audio/aac':    u'aac',
    u'audio/mp4':    u'm4a',
    u'audio/mpeg':   u'mp3',
    u'audio/ogg':    u'oga',
    u'audio/wav':    u'wav',
    u'audio/webm':   u'webm',
    u'audio/x-pn-realaudio':u'ra',
    u'application/x-pn-realaudio':u'ram',
    u'audio/basic':  u'snd',
    u'audio/x-wav':  u'wav'
    }
subtitle_exts = [u'srt', u'idx', u'sub', u'ssa', u'ass']
info_exts = [u'nfo']
video_exts = [u'3g2', u'3gp', u'3gp2', u'asf', u'avi', u'divx', u'flv', u'm4v', u'mk2',
              u'mka', u'mkv', u'mov', u'mp4', u'mp4a', u'mpeg', u'mpg', u'ogg', u'ogm',
              u'ogv', u'qt', u'ra', u'ram', u'rm', u'ts', u'wav', u'webm', u'wma', u'wmv',
              u'iso', u'm2ts',u'mpa',u'mpe']
pic_exts = [u'bmp',u'gif',u'ico',u'ief',u'jpe',u'jpeg',u'jpg',u'pbm',u'pgm',u'png',u'pnm',u'ppm',
            u'ras',u'rgb',u'tif',u'tiff',u'xbm',u'xpm',u'xwd',u'jpg',u'pct',u'pic',u'pict']
audio_exts = [ u'aac',u'asf',u'mp4',u'm4a',u'mp1',u'mp2',u'mp3',u'mpg',u'mpeg',u'oga',u'ogg',u'wav',u'webm',
               u'.mp2',u'.mp3',u'.ra',u'.ram',u'.snd',u'.wav', u'.wma']


#random_data = os.urandom(128)
#plexsession = hashlib.md5(random_data).hexdigest()[:16]
plexsession=unicode(uuid.uuid4())  #todo: hardcode this (see https://www.npmjs.com/package/plex-api)
socket.setdefaulttimeout(180)

debug_limitdld = False      #set to true during development to limit size of downloaded files
debug_outputxml = False     #output relevant XML when exceptions occur
debug_pretenddld = False     #set to true to fake downloading.  connects to Plex but doesn't save the file.
debug_pretendremove = False    #set to true to fake removing files
debug_plexurl = False        #set to true to output plex URL  (caution - will output Plex token)
minimum_to_watch_to_be_considerd_unwatched = 0.90        #minimum % to have watched an episode otherwise will be marked as unwatched todo: configurable
verbose = 1

plextoken=""

print "PlexDownloader - v0.07"

class MovieDownloader(object):
    class NoConfig(Exception):
        pass
    def __init__(self, num):
        tc = "movietranscode"
        cfg = "movies"
        if num > 0:
            tc += unicode(num)
            cfg += unicode(num)

        if not parser.has_section(cfg) or not parser.has_section(tc):
            #print "MovieDownloader %d - aborting" % num
            raise MovieDownloader.NoConfig("No config section")

        self.transcodeactive = parser.get(tc,'active')
        self.height = parser.get(tc,'height')
        self.width = parser.get(tc,'width')
        self.bitrate = parser.get(tc,'maxbitrate')
        self.quality = parser.get(tc,'videoquality')

        self.plexid = parser.get(cfg, 'plexid')
        self.location = parser.get(cfg, 'movielocation')
        self.itemfile = parser.get(cfg, 'moviefile')
        self.sync = parser.get(cfg, 'fullsync')
        self.active = parser.get(cfg, 'active')
        self.unwatched = parser.get(cfg,'unwatched')
        self.structure = parser.get(cfg,'folderstructure')
        #print "MovieDownloader %d - success" % num
        print "Syncing Movies to %s" % (self.location)

    def isactive(self):
        if self.active == "enable": return True
        return False

    def search(self):
        if not os.path.exists(self.location) or not os.path.isdir(self.location):
            print "Error: Path not located.  Create '%s' first." % (self.location)
            return
        wantedlist, skiplist = ReadItemFile(self.itemfile)
        if len(wantedlist) > 0:
            print unicode(len(wantedlist)) + " Movies Found in Your Wanted List..."
        if len(skiplist) > 0:
            print unicode(len(skiplist)) + " Movies Found in Your Skip List..."
        xmldoc = minidom.parse(urllib.urlopen(constructPlexUrl("/library/sections/"+unicode(self.plexid)+"/all")))
        itemlist = xmldoc.getElementsByTagName('Video')
        print unicode(len(itemlist)) + " Total Movies Found"
        syncedItems = 0
        failedItems = 0
        for item in itemlist:
            title = geta(item, 'title')
            #title = re.sub(r'[^\x00-\x7F]+',' ', title)
            title = re.sub(r'\&','and', title)
            title = title.strip()
            itemkey = geta(item, 'key')
            try:
                year = geta(item, 'year')
            except Exception as e:
                year="Unknown"
            try:
                #checks to see if view count node is available
                viewcount = geta(item, 'viewCount')
            except Exception as e:
                #if fails to find viewCount will notify script that it can continue
                viewcount = "unwatched"
            #checks if user wants unwatched only
            if self.unwatched=="enable":
                if viewcount=="unwatched":
                    if verbose: print title + " ("+year+") is unwatched..."
                else:
                    if verbose: print title + " ("+year+") is watched... skipping!"
                    continue
            itemname = title + " ("+year+")"
            if (itemname not in skiplist) and ((itemname in wantedlist) or (self.sync =="enable")):
                try:
                    parts = getMediaContainerParts(itemkey)
                    if parts:
                        #skip files that already exist
                        parts [:] = [p for p in parts if not self.exists(itemname,p) ]
                        if parts:
                            self.download(itemname,itemkey,parts)
                            syncedItems += 1
                except Exception as e:
                    failedItems += 1
                    print "Error syncing " + itemname + ".  Skipping..."
                    print(traceback.format_exc())
                    if debug_outputxml: print item.toprettyxml(encoding='utf-8')
            else:
                if verbose: print itemname + " Not Found in Wanted List."
        if syncedItems > 0 or failedItems > 0:
            print "Movie sync complete: %d downloaded  %d errors" % (syncedItems, failedItems)

    #checks if a movie exists.  Handles both self.structure choices
    #returns full path to file if it exists, None if it does not.
    #Any valid video extension is considered found movie
    def exists(self, itemname,part):
        if "subtitle" in part:
            #set filepath to complete path including extension
            filepath=self.fullfilepath(itemname,part, extension=part["container"])
        else:
            filepath=self.fullfilepath(itemname,part)
        folder=os.path.dirname(filepath)
        filename=os.path.basename(filepath)
        if os.path.isdir(folder):
            for f in os.listdir(folder):
                if f.lower().startswith(filename.lower()) and os.path.isfile(os.path.join(folder,f)):
                    if "subtitle" in part:  #exact match
                        return os.path.join(folder,f)
                    elif isValidVideoFile(f):
                        return os.path.join(folder,f)
                    else:
                        #print "Located " + f + " but is invalid extension"
                        pass
        return None

    #Path format of "self.location/movie name (year)/videos"
    #"server" structure uses the foldername and filename of the Plex server"
    #"default" structure uses generated folder and filenames
    #returns full filepath.  makes it all filesystem name-safe
    def fullfilepath(self, itemname,part,extension=None):
        if self.structure == "server":
            f = os.path.join(self.location, getFilesystemSafeName(part['foldername']), getFilesystemSafeName(os.path.splitext(part['filename'])[0]))
        else:
            f = os.path.join(self.location, getFilesystemSafeName(itemname), getFilesystemSafeName(itemname))
            if part and (not "subtitle" in part) and ("total" in part):  #only true for video files when there is more then 1 part
                f=f+u".pt"+unicode(part['num'])
        if extension:
            f += "."+getFilesystemSafeName(extension)
        return unicode(f)

    def download(self,itemname,plexkey,parts):
        plexsession = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(16))
        #plexsession = "z9fja0pznf40anzd"
        for counter, part in enumerate(parts):
            msg = itemname+"..."
            if len(parts) > 1:
                msg += " Item %d of %d" % (counter+1, len(parts))
            if "subtitle" in part:
                print "Downloading subtitle "+ msg
                link = constructPlexUrl(part['key'])
                if not retrieveMediaFile(link, self.fullfilepath(itemname,part),extension=part["container"],overwrite=False):
                    print "Subtitle file not downloaded"
            elif self.transcodeactive=="enable":
                print "Downloading transcoded "+ msg
                link = getTranscodeVideoURL(plexkey,self.quality,self.width, self.height, self.bitrate,plexsession,plextoken,counter)
                if not retrieveMediaFile(link, self.fullfilepath(itemname,part),overwrite=False):
                    print "Video not transcoded"
            else:
                print "Downloading "+ msg
                link = constructPlexUrl(part['key'])
                ext = os.path.splitext(part['filename'])[1][1:] #override
                if not retrieveMediaFile(link, self.fullfilepath(itemname,part),extension=getFilesystemSafeName(ext),overwrite=False):
                    print "Video not downloaded"

class TvDownloader(object):
    class NoConfig(Exception):
        pass
    def __init__(self, num):
        tc = "tvtranscode"
        cfg = "tvshows"
        if num > 0:
            tc += unicode(num)
            cfg += unicode(num)

        if not parser.has_section(cfg) or not parser.has_section(tc):
            raise TvDownloader.NoConfig("No config section")

        self.transcodeactive = parser.get(tc,'active')
        self.height = parser.get(tc,'height')
        self.width = parser.get(tc,'width')
        self.bitrate = parser.get(tc,'maxbitrate')
        self.quality = parser.get(tc,'videoquality')

        self.plexid = parser.get(cfg, 'plexid')
        self.itemfile = parser.get(cfg, 'tvfile')
        self.type = parser.get(cfg, 'tvtype')
        self.location = parser.get(cfg, 'tvlocation')
        self.sync = parser.get(cfg, 'fullsync')
        self.active = parser.get(cfg, 'active')
        self.delete = parser.get(cfg, 'autodelete')
        self.unwatched = parser.get(cfg,'unwatched')
        self.structure = parser.get(cfg,'folderstructure')
        self.exactnamematch = False   #for server mode, filenames must match exactly (except for extension)
        #print "MovieDownloader %d - success" % num
        print "Syncing TV to %s" % (self.location)

    def isactive(self):
        if self.active == "enable": return True
        return False

    def search(self):
        if not os.path.exists(self.location) or not os.path.isdir(self.location):
            print "Error: Path not located.  Create '%s' first." % (self.location)
            return
        wantedlist, skiplist = ReadItemFile(self.itemfile)
        if len(wantedlist) > 0:
            print unicode(len(wantedlist)) + " TV Shows Found in Your Wanted List..."
        if len(skiplist) > 0:
            print unicode(len(skiplist)) + " TV Shows Found in Your Skip List..."
        xmldoc = minidom.parse(urllib.urlopen(constructPlexUrl("/library/sections/"+self.plexid+"/all")))
        itemlist = xmldoc.getElementsByTagName('Directory')
        print unicode(len(itemlist)) + " Total TV Shows Found"
        syncedItems = 0
        failedItems = 0
        removedItems = 0
        for item in itemlist:
            title = geta(item, 'title')
            #title = re.sub(r'[^\x00-\x7F]+',' ', title)
            title = re.sub(r'\&','and', title)
            title = title.strip()
            itemkey = geta(item, 'key')
            #safeitemname = getFilesystemSafeName(title)
            if (title not in skiplist) and ((title in wantedlist) or (self.sync =="enable")):
                if verbose: print title + " Found in Wanted List"
                xmlseason = minidom.parse(urllib.urlopen(constructPlexUrl(itemkey)))
                seasonlist = xmlseason.getElementsByTagName('Directory')
                #construct list of episodes to sync
                episodelist = []
                if (self.type=="all") or (self.type=="episode"):    #download everything
                    for season in seasonlist:
                        if season.hasAttribute('index'):   #skip "allSeasons"
                            xmlepisode = minidom.parse(urllib.urlopen(constructPlexUrl(geta(season, 'key'))))
                            for e in xmlepisode.getElementsByTagName('Video'):
                                e.setAttribute('seasonIndex', geta(season, 'index'))
                                episodelist.append(e)
                elif (self.type=="recent"): #download latest season
                    xmlepisode = minidom.parse(urllib.urlopen(constructPlexUrl(geta(seasonlist[len(seasonlist)-1], 'key'))))
                    for e in xmlepisode.getElementsByTagName('Video'):
                        e.setAttribute('seasonIndex', geta(seasonlist[len(seasonlist)-1], 'index'))
                        episodelist.append(e)
                #if not episodelist: continue
                if self.type == "episode":
                    numEpisodes = 2  #number of episodes to retain.  todo: make this configurable
                    #shrink to just last N episodes.
                    episodelist = sorted(episodelist, key = lambda x: (int(geta(x,'seasonIndex')), int(geta(x,'index'))))[0-numEpisodes:]
                if verbose: print "    Syncing %d episodes for %s" %(len(episodelist), title)
                for counter, episode in enumerate(episodelist):
                    try:
                        episodekey = geta(episode, u'key')
                        episodeindex = geta(episode, u'index')
                        episodetitle = geta(episode, u'title')
                        episodetitle = episodetitle.strip()
                        seasonindex = geta(episode, 'seasonIndex')  #Added during list creation
                        duration = long(geta(episode, 'duration'))
                        this_minimum_to_watch = long(duration * minimum_to_watch_to_be_considerd_unwatched)
                        if verbose: print "Analyzing Episode " + episodeindex
                        ## if debug_outputxml: print episode.toprettyxml()
                        ## if verbose: print "    Duration " + str(duration)
                        ## if verbose: print "    Minimum to watch " + str(this_minimum_to_watch)
                        try:
                            #checks to see if episode has been viewed node is available
                            viewcount = long(geta(episode, 'lastViewedAt'))
                        except Exception as e:
                            #if fails to find lastViewedAt will notify script that tv is unwatched
                            viewcount = "unwatched"
                        try:
                            viewOffset = long(geta(episode, 'viewOffset'))
                            if viewOffset < this_minimum_to_watch: viewcount = "partial"
                        except Exception as e:
                            #if fails to find viewOffset will notify script that tv is unwatched
                            viewOffset = 0
                        ## if verbose: print "    viewOffset " + str(viewOffset)
                        ## if verbose: print "    viewcount: " + str(viewcount)
                        #checks if user wants unwatched only
                        if self.unwatched=="enable":
                            if viewcount=="unwatched":
                                if verbose: print "    Episode is unwatched..."
                            elif viewcount=="partial":
                                if verbose: print ("    Episode is {:.0%} < {:.0%} watched... INCLUDING ! ").format(float(viewOffset)/float(duration),minimum_to_watch_to_be_considerd_unwatched)
                            else:
                                if verbose: print "    Episode is watched... skipping!"
                                #todo: remove files that are watched when tvtype = all
                                continue
                        parts = getMediaContainerParts(episodekey)
                        if parts:
                            #skip files that already exist
                            parts [:] = [p for p in parts if not self.exists(title,seasonindex,episodeindex,p) ]
                            if parts:
                                self.download(title,seasonindex,episodeindex,episodetitle,episodekey,parts)
                                syncedItems += 1
                    except Exception as e:
                        failedItems += 1
                        print "    Error syncing episode.  Skipping..."
                        print(traceback.format_exc())
                        if debug_outputxml: print episode.toprettyxml(encoding='utf-8')
                #remove old episodes
                if self.type=="episode" and self.delete=="enable":
                    if episodelist:
                        #remove anything older then the oldest item in the list
                        (r,f) = self.removeoldepisodes(title, geta(episodelist[0],'seasonIndex'),geta(episodelist[0],'index'))
                        removedItems += r
                        failedItems += f
            else:
                print title + " Not Found in Wanted List."
        if syncedItems > 0 or failedItems > 0 or removedItems > 0:
            print "TV synch complete: %d downloaded, %d removed, %d errors" % (syncedItems, removedItems, failedItems)

    #removes all episodes and related files OLDER then season+episode
    def removeoldepisodes(self, title, season, episode):
        dirs = []
        season=int(season)
        episode=int(episode)
        removedItems = 0
        failedItems = 0

        if self.structure == "server":
            #find dirs to check first to avoid recursion
            folder = os.path.join(self.location, getFilesystemSafeName(title))
            pattern = '(?ix)season\s*(\d{1,3})'
            r = re.compile(pattern)
            if os.path.isdir(folder):
                for f in os.listdir(folder):
                    result = r.search(f)
                    if result and os.path.isdir(os.path.join(folder,f)):
                        s = int(result.groups()[0])
                        if s <= season:
                            dirs.append(os.path.join(folder, f))
                    elif f.lower() == "specials" and os.path.isdir(os.path.join(folder,f)):
                        dirs.append(os.path.join(folder, f))  #always append Specials folder since it's season 0
        else:
            dirs.append(os.path.join(self.location, getFilesystemSafeName(title)))
        #Walk folder and look for files matching the 1x1,s2e2,etc format or s1e01-e04 format
        pattern = '(?ix)(?:s)?(\d{1,3})(?:e|x)(\d{1,3})(?:-[ex](\d{1,3}))?(?:[\s\.\-,_])'
        r = re.compile(pattern)
        for folder in dirs:
            if os.path.isdir(folder):
                for f in os.listdir(folder):
                    result = r.search(f)
                    if result and os.path.isfile(os.path.join(folder,f)):
                        s = int(result.groups()[0])
                        e = int(result.groups()[1])
                        e1 = int(result.groups()[2]) if result.groups()[2] else None
                        if  (s < season) or \
                            ((s == season) and \
                                ((not e1) and e < episode) or \
                                ((e1) and (e < episode and e1 < episode )) \
                             ):
                            if isValidVideoFile(f) or isValidAudioFile(f) or isValidSubtitleFile(f):
                                try:
                                    fn = os.path.join(folder, f)
                                    print "Deleting old episode: " + fn
                                    if not debug_pretendremove: os.remove(fn)
                                    removedItems += 1
                                except Exception as e:
                                    failedItems += 1
                                    print "Could not delete old episode. Will try again on the next scan."
        return (removedItems, failedItems)

    #checks if a tv episode exists based on season/episode.  Used to filter out already downloaded items.
    #Processes differently depending on whether in server mode or not
    #For video files:
    #In server mode, will return True if filename.[video extension] exists
    #In default mode, will return True if there is a file with *season+episode*.[video extension]
    #Note that it will treat any video file (mp4, mkv, etc) as found in both modes!
    #For subtitles:
    #In server mode, will return True if filename.extension exists
    #In default mode, will return True if there is a file with *season+episode*.[calculated extension]
    #all is case-insensitive
    def exists(self,itemname,season,episode,part):
        season=int(season)
        episode=int(episode)
        dirs = []

        if self.exactnamematch:
            #in server mode, video filename must match exactly except for extension.
            #subtitles must match including extension
            filepath = self.basefilepath(itemname,season,episode,part)
            folder=os.path.dirname(filepath)
            filename=os.path.basename(filepath).lower()
            if os.path.isdir(folder):
                for f in os.listdir(folder):
                    if f.lower().startswith(filename) and os.path.isfile(os.path.join(folder,f)):
                        if "subtitle" in part:
                            if f.lower().endswith(part["container"].lower()):  #container includes "lan.[X.].ext"
                                return os.path.join(folder,f)
                        elif isValidVideoFile(f):
                            return os.path.join(folder,f)
                        else:
                            #print "Located " + f + " but is invalid extension"
                            pass
            return None
        elif self.structure == "server":
            #Check in all subfolders.  append all the first level sub folders.  We check every folder, every time.
            folder = os.path.join(self.location,getFilesystemSafeName(itemname))
            pattern = '(?ix)season\s*(\d{1,3})'
            r = re.compile(pattern)
            if os.path.isdir(folder):
                for f in os.listdir(folder):
                    result = r.search(f)
                    if result and os.path.isdir(os.path.join(folder,f)):
                        dirs.append(os.path.join(folder, f))
                    elif f.lower() == "specials" and os.path.isdir(os.path.join(folder,f)):
                        dirs.append(os.path.join(folder, f))  #always append Specials folder since it's season 0
        dirs.append(os.path.join(self.location,getFilesystemSafeName(itemname)))
        #Walk folder and look for files matching the 1x1,s2e2,etc format
        #also handle s1e01-e04 format
        pattern = '(?ix)(?:s)?(\d{1,3})(?:e|x)(\d{1,3})(?:-[ex](\d{1,3}))?(?:[\s\.\-,_])'
        r = re.compile(pattern)
        for folder in dirs:
            if os.path.isdir(folder):
                for f in os.listdir(folder):
                    result = r.search(f)
                    if result and os.path.isfile(os.path.join(folder,f)):
                        if (episode == int(result.groups()[1]) and season == int(result.groups()[0])) or \
                           (result.groups()[2] and (episode >= int(result.groups()[1]) and episode <= int(result.groups()[2]))): # process s1e01-e04 files
                            if "subtitle" in part:  #exact match on subtitle extension
                                if f.lower().endswith("."+unicode(part["container"].lower())):
                                    return os.path.join(folder,f)
                            elif isValidVideoFile(f):
                                return os.path.join(folder,f)
        return None

    #get the basic filename without extension or episode text. Used for finding existing files
    #"server" structure uses the foldername and filename of the Plex server"
    #"default" structure is "self.location/show name/"
    def basefilepath(self,itemname,season,episode,part):
        if self.structure == "server":
            return os.path.join(self.location, getFilesystemSafeName(itemname), getFilesystemSafeName(part['foldername']), getFilesystemSafeName(os.path.splitext(part['filename'])[0]))
        else:
            return os.path.join(self.location, getFilesystemSafeName(itemname), getFilesystemSafeName(itemname+" - s"+season+"e"+episode))

    #"server" structure uses the foldername and filename of the Plex server"
    #"default" structure is "self.location/show name/"
    #contents of part are used to determine if there should be a "ptX" appended  (not used in server mode)
    #returns full filepath.  makes it all filesystem name-safe
    def fullfilepath(self,itemname,season,episode,eptitle,part,extension=None):
        f = self.basefilepath(itemname, season, episode, part)
        if self.structure != "server":
            if eptitle:
                f += u" - "+eptitle
            if part and (not "subtitle" in part) and ("total" in part):  #only true for video files when there is more then 1 part
                f=f+u".pt"+unicode(part['num'])
        if extension:
            f = f+u"."+getFilesystemSafeName(extension)
        return unicode(f)

    def download(self,itemname,season,episode,eptitle,plexkey,parts):
        plexsession = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(16))
        #plexsession = "z9fja0pznf40anzd"
        #numparts = sum('subtitle' in p for p in parts)  #this is number of non-subtitle parts
        for counter, part in enumerate(parts):
            eptitle = getFilesystemSafeName(eptitle)
            msg = itemname + " s"+unicode(season).zfill(2)+"e"+unicode(episode).zfill(2)+"..."
            if len(parts) > 1:
                msg += " Item %d of %d" % (counter+1, len(parts))
            if "subtitle" in part:
                print "Downloading subtitle "+ msg
                link = constructPlexUrl(part['key'])
                if not retrieveMediaFile(link, self.fullfilepath(itemname,season,episode,eptitle,part),extension=part["container"],overwrite=False):
                    print "Subtitle file not downloaded"
            elif self.transcodeactive=="enable":
                print "Downloading transcoded "+ msg
                link = getTranscodeVideoURL(plexkey,self.quality,self.width, self.height, self.bitrate,plexsession,plextoken,counter)
                if not retrieveMediaFile(link, self.fullfilepath(itemname,season,episode,eptitle,part),overwrite=False):
                    print "Video file not transcoded"
            else:
                print "Downloading "+ msg
                link = constructPlexUrl(part['key'])
                ext = os.path.splitext(part['filename'])[1][1:] #override extension
                if not retrieveMediaFile(link, self.fullfilepath(itemname,season,episode,eptitle,part),extension=getFilesystemSafeName(ext),overwrite=False):
                    print "Video file not downloaded"

class MusicDownloader(object):
    class NoConfig(Exception):
        pass

    def __init__(self, num):
        cfg = "music"
        if num > 0:
            cfg += unicode(num)

        if not parser.has_section(cfg):
            raise MusicDownloader.NoConfig("No config section")

        self.plexid = parser.get(cfg, 'plexid')
        self.location = parser.get(cfg, 'musiclocation')
        self.itemfile = parser.get(cfg, 'musicfile')
        self.sync = parser.get(cfg, 'fullsync')
        self.active = parser.get(cfg, 'active')
        print "Syncing Music to %s" % (self.location)

    def isactive(self):
        if self.active == "enable": return True
        return False

    def search(self):
        if not os.path.exists(self.location) or not os.path.isdir(self.location):
            print "Error: Path not located.  Create '%s' first." % (self.location)
            return
        wantedlist, skiplist = ReadItemFile(self.itemfile)
        if len(wantedlist) > 0:
            print unicode(len(wantedlist)) + " Artists Found in Your Wanted List..."
        if len(skiplist) > 0:
            print unicode(len(skiplist)) + " Artists Found in Your Skip List..."
        xmldoc = minidom.parse(urllib.urlopen(constructPlexUrl("/library/sections/"+self.plexid+"/all")))
        itemlist = xmldoc.getElementsByTagName('Directory')
        print unicode(len(itemlist)) + " Total TV Artists Found"
        syncedItems = 0
        failedItems = 0
        for item in itemlist:
            title = geta(item, 'title')
            #title = re.sub(r'[^\x00-\x7F]+',' ', title)
            title = re.sub(r'\&','and', title)
            title = title.strip()
            itemkey = geta(item, 'key')
            if (title not in skiplist) and ((title in wantedlist) or (self.sync =="enable")):
                try:
                    if verbose: print title + " Found in Wanted List"
                    xmlseason = minidom.parse(urllib.urlopen(constructPlexUrl(itemkey)))
                    cdlist = xmlseason.getElementsByTagName('Directory')
                    for cd in cdlist:
                        cdtitle = geta(cd, 'title').strip()
                        if cd.hasAttribute('index'):   #skip "allSeasons"
                            xmlsong = minidom.parse(urllib.urlopen(constructPlexUrl(geta(cd, 'key'))))
                            #Get List of Songs
                            songlist=xmlsong.getElementsByTagName('Track')
                            #Check for duplicate song titles
                            numberTitles = False
                            songnames = [geta(s, 'title').strip() for s in songlist]
                            if any(songnames.count(x) > 1 for x in songnames):
                                numberTitles = True
                                print "Warning: Duplicate song titles in %s.  Adding track number at beginning of filename." % (title)
                            for counter,song in enumerate(songlist):
                                songtitle = geta(song, 'title').strip()
                                songrating = geta(song, 'ratingKey')
                                if songtitle=="":
                                    songtitle = songrating
                                if numberTitles:
                                    if song.hasAttribute('index'):
                                        songtitle = unicode(geta(song, 'index')).zfill(3) + " " + songtitle
                                    else:
                                        songtitle = unicode(counter).zfill(3) + " " + songtitle
                                parts = getMediaContainerParts(geta(song, 'key'))
                                if parts:
                                    #filter out files that already exist
                                    parts [:] = [p for p in parts if not self.exists(title,cdtitle,songtitle,p) ]
                                    if parts:
                                        self.download(title,cdtitle,songtitle,parts)
                                        syncedItems += 1
                except Exception as e:
                    failedItems += 1
                    print "Error syncing " + title + ".  Skipping..."
                    print(traceback.format_exc())
                    if debug_outputxml: print item.toprettyxml(encoding='utf-8')
            else:
                print title + " Not Found in Wanted List."
        if syncedItems > 0 or failedItems > 0:
            print "Music synch complete: %d downloaded, %d errors" % (syncedItems, failedItems)

    #returns full filepath.  makes it all filesystem name-safe
    def fullfilepath(self,artist,cd,song,part,extension=None):
        f = os.path.join(self.location, getFilesystemSafeName(artist), getFilesystemSafeName(cd), getFilesystemSafeName(song))
        if part and (not "subtitle" in part) and ("total" in part):  #only true for video files when there is more then 1 part
            f=f+u".pt"+unicode(part['num'])
        if extension:
            f = f+u"."+extension
        return unicode(f)

    def exists(self,artist,cd,song,part):
        filepath=self.fullfilepath(artist,cd,song,part)
        folder=os.path.dirname(filepath)
        filename=os.path.basename(filepath)
        if os.path.isdir(folder):
            for f in os.listdir(folder):
                if f.lower().startswith(filename.lower()) and os.path.isfile(os.path.join(folder,f)):
                    if isValidAudioFile(f):
                        return os.path.join(folder,f)
                    else:
                        #print "Located " + f + " but is invalid extension"
                        pass
        return None

    def download(self,artist,cd,song,parts):
        for counter, part in enumerate(parts):
            if len(parts) > 1:
                msg = cd + " Song: "+song+"..."+"... Part %d of %d" % (counter+1, len(parts))
            else:
                msg = cd + " Song: "+song+"..."
            #this is good for both audio files and any future subtitles (future-proof for lyrics)
            print "Downloading "+ msg
            link = constructPlexUrl(part['key'])
            ext = part['container']  #use whatever the server said it is first
            if not ext: ext = os.path.splitext(part['filename'])[1][1:]
            if not retrieveMediaFile(link, self.fullfilepath(artist,cd,song,part),extension=getFilesystemSafeName(ext),overwrite=False):
                print "Music file not downloaded"



def isValidVideoFile(filename):
    try:
        ext = os.path.splitext(filename)[1].lower()[1:]
        if ext in video_exts:
            return True
        return False
    except Exception as e:
        return False

def isValidAudioFile(filename):
    try:
        ext = os.path.splitext(filename)[1].lower()[1:]
        if ext in audio_exts:
            return True
        return False
    except Exception as e:
        return False

def isValidSubtitleFile(filename):
    try:
        ext = os.path.splitext(filename)[1].lower()[1:]
        if ext in subtitle_exts:
            return True
        return False
    except Exception as e:
        return False

#Itemfile is list of shows to include/exclude.  Exclude by adding a "!" at beginning of show name.
#Any blank line or line beginning with a hash mark are ignored.
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

def getTranscodeVideoURL(plexkey,quality,width,height,bitrate,session,token,partindex=0):
    clientuid = uuid.uuid4()
    clientid = clientuid.hex[0:16]
    link = (url+"/video/:/transcode/universal/start?path=http%3A%2F%2F127.0.0.1%3A32400"+plexkey+
            "&mediaIndex=0"+
            "&partIndex="+unicode(partindex)+
            "&protocol=http"+
            "&offset=0"+
            "&fastSeek=1"+
            "&directPlay=0"+
            "&directStream=1"+
            "&videoQuality="+quality+
            "&videoResolution="+width+"x"+height+
            "&maxVideoBitrate="+bitrate+
            "&subtitleSize=100"+
            "&audioBoost=100"+
            "&session="+session+
            #"&X-Plex-Client-Profile-Extra=add-transcode-target-audio-codec(type%3DvideoProfile%26context%3Dstreaming%26protocol%3Dhls%26audioCodec%3Daac)"+  #restrict audiocodec to aac
            "&X-Plex-Client-Identifier="+clientid+
            "&X-Plex-Product=Plex Web"+
            "&X-Plex-Device=Plex Downloader"+
            "&X-Plex-Platform=HTML TV App"+
            "&X-Plex-Platform-Version=43.0"+
            "&X-Plex-Version=2.4.9"
            )
    if myplexstatus=="enable":
        link = link+"&X-Plex-Token="+token
    if debug_plexurl: print link
    return link

#hls flow

def tell_me_about(s): return (type(s), s)

#Downloads link to file.  Will detect the type of video file and add the
#correct extension to file.  Will work with multi-part video files.
#Set extension to non-None to override the automatic detection and use the passed extension
#Will overwrite existing files if "overwrite==True"
#Returns True on download, False on no-download or failure
def retrieveMediaFile(link,filename,extension=None,overwrite=False):
    try:
        #if verbose: print "storing link to: " + filename
        cleanup = False  #gracefully cleanup failed transcodes so we can try again
        if not os.path.exists(os.path.split(filename)[0]):
            os.makedirs(os.path.split(filename)[0])
        epfile = urllib.urlopen(link)
        if not extension:
            mimetype = epfile.info().type.lower()
            mimetype = mimetype.replace('content-type: ','')  #plex has bug that returns "Content-Type" as part of the Content-Type.  Doh!
            if mimetype in mimetypes:
                extension = mimetypes[mimetype]
            else:
                print "Warning: Unknown mimetype for file (%s) Using mpg as default" % (mimetype)
                extension = "mpg"  #use this as default
        filename=filename+"."+extension.lower()
        #if verbose: print "Downloading "+link+" ==> "+filename
        if verbose: print "Downloading "+filename
        if debug_pretenddld: return True
        if overwrite or (not os.path.isfile(filename)):
            #print tell_me_about(filename.encode("utf8"))
            #print tell_me_about(filename.encode("cp1252"))
            #print tell_me_about(filename.encode("cp1252").decode("utf8"))
            #filename = filename.encode("cp1252").decode("utf-8")
            with open(filename, "wb") as fp:
                cleanup = True
                while True:
                    if debug_limitdld:
                        #chunk = epfile.read(1024)  #1K buffer
                        #fp.write(chunk)
                        break
                    else:
                        chunk = epfile.read(1024*1024)  #1MB buffer
                        if not chunk: break
                        fp.write(chunk)
            return True
        else:
            #this shouldn't really happen much.  Existing files should be caught before file is downloaded.
            #Can happen when there are two video files for a single Plex video that are the same except for extension.
            print "File %s already exists. Skipping download." % (filename)
            return False
    except (KeyboardInterrupt, SystemExit):
        try:
            if cleanup: os.remove(filename)
        except:
            pass
        raise KeyboardInterrupt()
    except Exception as e:
        print "Something went wrong transcoding video... Deleting and retrying on next scan!"
        print "Something went wrong: " + unicode(e)
        print(traceback.format_exc())
        try:
            if cleanup: os.remove(filename)
        except:
            pass

    return False

def constructPlexUrl(key):
    http = unicode(url) + unicode(key)
    if myplexstatus=="enable":
        http +="?X-Plex-Token="+plextoken
    if debug_plexurl: print http
    return http

#Plex/minidom don't get along well with character encoding.  This is a hack to fix errors that you get with extended characters.
from types import *
def geta(o, attr):
    try:
        a = o.getAttribute(attr)
        if not a:
            return u''
        return a
    except Exception as e:
        print "Something went wrong get attribute: " + unicode(e)
        print(traceback.format_exc())
        print tell_me_about(a)
        return u''

#Loads the passed key from node.
#'container' is sometimes None
def getMediaContainerParts(key):
    try:
        xmlmedia = minidom.parse(urllib.urlopen(constructPlexUrl(key)))
        partindex = xmlmedia.getElementsByTagName('Part')
        parts = []
        sub_parts = []
        for counter, partitem in enumerate(partindex):
            downloadkey = geta(partitem, 'key')  #key goes directly to file
            filepath = urllib2.unquote(geta(partitem, 'file'))
            #filepath = urllib2.unquote(partitem.attributes['file'].value)
            filepath = filepath.encode("cp1252",errors='replace').decode("utf-8",errors='replace')  #Re-correct for extended characters
            filename = os.path.basename(filepath)
            foldername = os.path.dirname(os.path.realpath(filepath))
            foldername = os.path.basename(os.path.realpath(foldername))
            container = geta(partitem, 'container')  #not always present
            parts.append({"num":counter+1, "key":downloadkey, "filename":filename,"foldername":foldername, "container":container})
            #Add any subtitle files
            try:  #seperate try block so failure is limited to subtitles (which can be messy)
                streamindex = partitem.getElementsByTagName('Stream')
                sub_counts = {}
                #filter just the streams that we want.  (streamType == 3 for subtitle and 'key' when there's a seperate file)
                streamindex [:] = [s for s in streamindex if ((geta(s, "streamType") == "3") and geta(s, "key")) ]
                for stream in streamindex:
                    if geta(stream, "codec").lower() in subtitle_exts:
                        lang = geta(stream, "languageCode").lower()
                        if not lang:
                            lang = "unk"
                            streamcontainer = ""
                        else:
                            streamcontainer = lang + "."
                        sub_counts[lang] = 0 if not lang in sub_counts else sub_counts[lang] + 1
                        if int(sub_counts[lang]) > 0:
                            streamcontainer += unicode(sub_counts[lang]) + "."
                        streamcontainer += geta(stream,"codec").lower()
                        sub_parts.append({"num":sub_counts[lang], "key":geta(stream, "key"), "filename":filename,"foldername":foldername, "container":streamcontainer, "subtitle":True})
            except Exception as e:
                print "Error while getting subtitles"
                print(traceback.format_exc())
        #When more then 1 part, add total number of parts to each part record for the non-subtitle files
        if len(parts) > 1:
            for n in range(len(parts)):
                parts[n]["total"] = len(parts)
        return parts+sub_parts
    except Exception as e:
        print "Error while getting media parts"
        print(traceback.format_exc())
        return None

def getFilesystemSafeName(s):
    s = re.sub(r'[\\/:"*?<>|"]+',"",s)
    return s

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


def photoSearch():
    pictureopen = open(picturefile,"r")
    pictureread = pictureopen.read()
    picturelist= pictureread.split("\n")
    pictureopen.close()
    print unicode(len(picturelist)-1) + " Albums Found in Your Wanted List..."

    if myplexstatus=="enable":
        pichttp=url+"/library/sections/"+pictureid+"/all"+"?X-Plex-Token="+plextoken
    else:
        pichttp=url+"/library/sections/"+pictureid+"/all"
    website = urllib.urlopen(pichttp)
    xmldoc = minidom.parse(website)
    itemlist = xmldoc.getElementsByTagName('Directory')
    print unicode(len(itemlist)) + " Total Albums Found"
    for item in itemlist:
        albumtitle = geta(item, 'title')
        #albumtitle = re.sub(r'[^\x00-\x7F]+',' ', albumtitle)
        albumtitle = re.sub(r'\&','and', albumtitle)
        albumtitle = albumtitle.strip()
        albumkey = geta(item, 'key')
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

                pictitle= geta(pics, 'title').strip()
                partalbum=pics.getElementsByTagName('Part')

                piccontainer = geta(partalbum[0], 'container')
                pickey = geta(partalbum[0], 'key')

                if myplexstatus=="enable":
                    piclink=url+pickey+"?X-Plex-Token="+plextoken
                else:
                    piclink=url+pickey
                print pictitle + albumtitle
                photoDownloader(albumtitle,pictitle,piclink,piccontainer)

        else:
            print albumtitle + " Album Not Found in Wanted List."


#Load all sections from config file
movies = []
try:
    while True: movies.append(MovieDownloader(len(movies)))
except MovieDownloader.NoConfig: pass
tvshows = []
try:
    while True: tvshows.append(TvDownloader(len(tvshows)))
except TvDownloader.NoConfig: pass
music = []
try:
    while True: music.append(MusicDownloader(len(music)))
except MusicDownloader.NoConfig: pass

while True:
    try:
        if myplexstatus=="enable":
            plextoken = myPlexSignin(myplexusername,myplexpassword)
        if myplexstatus=="enable" and plextoken=="":
            print "Failed to login to myPlex. Please disable myPlex or enter your correct login."
            exit()
        for x in tvshows:
            if(x.isactive()):
                x.search()
        for x in movies:
            if(x.isactive()):
                x.search()
        for x in music:
            if(x.isactive()):
                x.search()
        if pictureactive=="enable":
            photoSearch()

        print "Plex Download completed at "+ strftime("%Y-%m-%d %H:%M:%S")
        print "Sleeping "+unicode(sleepTime)+" Seconds..."
        time.sleep(sleepTime)
    except Exception as e:
        print "Something went wrong: " + unicode(e)
        print(traceback.format_exc())
        print "Plex Download failed at "+ strftime("%Y-%m-%d %H:%M:%S")
        print "Retrying in "+unicode(sleepTime)+" Seconds..."
        time.sleep(sleepTime)
