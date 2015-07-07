PlexDownloader
==============
Configuring PlexDownloader:

1)Edit the user.ini with information that is relevant to your install.

2)If you are downloading/syncing remotely you must enter your myplex information and enable myplex.

3)Start by running "python plexdl.py".

You can find your movie/music/tv/photo section ID by visiting your Plex Web and going to the category you want to sync.

http://192.168.3.5/web/index.html#!/server/.../section/2

The ID you are looking for is the number at the end which in the above example is 2.

You can also find your content section ID by visiting:
http://localhost:32400/library/sections/


[User.Ini Options]

[general]

sleeptime = time in seconds that you want to wait between checking for new content. Default is 600 seconds (10 minutes).

plexurl = enter your IP here make sure to have no "/" at the end of the ip. For example http://127.0.0.1:32400

[webui]

status=enable|disable (web manager for sync items)

port=8585 (default is 8585 but you can change to whatever port you want)

[myplex]

status=disable|enable (default is disable)

username=user@email.com (your myplex email)

password=password (your myplex password)

[tvshows]

active = enable|disable (Activates the category so it will be scanned)

plexid = 4 (your tv show section plex id)

tvfile = tvshows.txt (this is the list of the tv show you want to sync. one tv show per line. Enter exactly how you see it in plex.)

tvtype = episode|recent|all (recent will download on the most current season. all will download every season)

tvlocation = /Users/plexdl/Downloads/TV Shows/ (download location for your synced tvshows EX: C:/Downloads/TV Shows/)

fullsync = enable|disable [Will download everything it finds, will follow tvtype so you can sync the most recent of every show]

autodelete = enable|disable [Will automatically delete old episodes]

folderstructure = default|server [server uses plex server naming convention - /Season X/Show s1e1 - desc.mkv]

[movies]

active = enable|disable (Activates the category so it will be scanned)

plexid = 5 (your movie section plex id)

moviefile = movies.txt (this is the list of wanted movies you want to sync. One movie per line. Format: Movie (year) EX: Avatar (2009)

movielocation = /Users/plexdl/Downloads/Movies/ (download location for your synced movies. EX: C:/Downloads/Movies/)

fullsync = enable|disable (Will download everything it finds)


[music]

active = enable|disable (Activates the category so it will be scanned)

plexid = 6 (your music section plex id)

musicfile = music.txt (your wanted list of music. Include only artists one per line.)

musiclocation = /Users/plexdl/Downloads/Music/ (download location for your synced music)

fullsync = enable|disable (will download everything it finds)

[pictures]

active = enable|disable (Activates the category so it will be scanned)

plexid = 7 (your pictures section plex id)

picturefile = pictures.txt (your wanted list of pictures. Include only albums one per line.)

picturelocation = /Users/plexdl/Downloads/Pictures/ (download location for your synced pictures)

fullsync = enable|disable (will download everything it finds)

EXAMPLES:

[tvshows.txt]

Warehouse 13

Eureka

[movies.txt]

Avatar (2009)

[music.txt]

The Beatles

[pictures.txt]

Family Trip To France
