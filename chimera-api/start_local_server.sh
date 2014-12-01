#!/usr/bin/env bash

echo 'Killing previously running servers, if any...'
kill -9 $(ps aux | grep 'chimera-api/env/bin/python ./listen.py' | awk '{print $2}')

source ./env/bin/activate
rm -f *"_server.log"
ports=(6001 6002 6003 6004 6005)
for port in "${ports[@]}"
do
    echo "Starting on $port"
    ./listen.py $port > $port"_server.log" 2>&1 &
done
sleep 2
tail -f *"_server.log"

