PlexDownloader
==============
Configuring PlexDownloader:

1)Edit the user.ini with information that is relevant to your install.

2)If you are downloading/syncing remotely you must enter your myplex information and enable myplex.

3)Start by running "python plexdl.py".

You can find your movie and tv show section ID by visiting your Plex Web and going to the category you want to sync.

http://192.168.3.5/web/index.html#!/server/.../section/2

The ID you are looking for is the number at the end which in the above example is 2.


[User.Ini Options]

[general]

sleeptime = time in seconds that you want to wait between checking for new content. Default is 600 seconds (10 minutes).

plexurl = enter your IP here make sure to have no "/" at the end of the ip. For example http://127.0.0.1:32400

[myplex]

status=disable|enable (default is disable)

username=user@email.com (your myplex email)

password=password (your myplex password)

[tvshows]

plexid = 2 (your tv show section plex id)

tvfile = tvshows.txt (this is the list of the tv show you want to sync. one tv show per line. Enter exactly how you see it in plex.)

tvtype = recent|all (recent will download on the most current season. all will download every season)

tvlocation = /Users/plexdl/Downloads/TV Shows/ (download location for your synced tvshows EX: C:/Downloads/TV Shows/)

[movies]

plexid = 1 (your movie section plex id)

moviefile = movies.txt (this is the list of wanted movies you want to sync. One movie per line. Format: Movie (year) EX: Avatar (2009)

movielocation = /Users/plexdl/Downloads/Movies/ (download location for your synced movies. EX: C:/Downloads/Movies/)

EXAMPLES:

[tvshows.txt]

Warehouse 13

Eureka

[movies.txt]

Avatar (2009)
