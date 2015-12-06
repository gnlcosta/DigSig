# DigSig
Digital Signage

Open source, web-based digital signage player.

The media player is able to download the contents from the web and, using a playlist, it plays the videos or the images following the timing described by the play list.

# Playlist: XML structure
DigSig download from a Server the playlist that it will use to play the media. In the playlist are described:
 * the media type (video or image)
 * where downlaod the media
 * when play the medie
 * the uniquie ID of the media
There is not limit about the number of the elements (media) of the playlist. Each playlist can have a ID that identify it, this ID is used by DigSig to send reports to the server.

An example of play list:
```
<?xml version="1.0" encoding="UTF-8"?>
<adv>
    <id>0000001</id>
    <elem>
	    <id>0000001</id>
	    <type>video</type>
        <url>http://www.sample-videos.com/video/mp4/480/big_buck_bunny_480p_1mb.mp4</url>
        <start>37737373</start>
    </elem>
    <elem>
	    <id>0000002</id>
	    <type>video</type>
        <url>https://vimeo.com/78961286/download?t=1449425297&v=203684545&s=54b42788f7045fb6cb0643b7becc2692ef2cef7474959ad9e2b13cf1744a8d31</url>
        <start>37737373</start>
    </elem>
    <next_req>10</next_req>
</adv>
```
# Install
The program is composed only by a single Python script. To work the script requires some applications.
To launche the script:
`./digsig.py`

## Dependencies
In the system must be installed:
 * mplayer
 * xdotool
 * feh
 
## Raspberry

## Beaglebone Black

# Configuration
The configuration file is composed by a JSON file. In the JSON file there are two fieds:
 * servel_url : the URL where the DigSig can download the play list
 * id: the identification of the system that is running the script (may be useful server side)
An example:
```
{
    "servel_url": "http://localhost/ds_server_example.php",
    "id": "18:32:ed:0a:73:f7"
}
```

# Server side

# License
GNU AFFERO GENERAL PUBLIC LICENSE
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
