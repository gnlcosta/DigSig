#! /bin/bash

sleep 15
export DISPLAY=':0'
export XAUTHORITY=/home/pi/.Xauthority
xset s off
xset -dpms
xdotool mousemove 1920 1080

#cd /opt/ds
while true; do
    now=$(date +%s)
    to=$((86400 - $(($now % 86400))))
    (sleep $to; pkill -9 digsig.py; pkill -9 mplayer) &
    ./digsig.py
    pkill mplayer
    sleep 1
done
