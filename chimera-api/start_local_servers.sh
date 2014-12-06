#!/usr/bin/env bash

echo 'Killing previously running servers, if any...'
kill -9 $(ps aux | grep 'chimera-api/env/bin/python ./server.py' | awk '{print $2}')

source ./env/bin/activate
rm -f *"_server.log"
ports=(6001 6005 6002 6004 6003)
for port in "${ports[@]}"
do
    echo "Starting on 127.0.0.1:$port"
    ./server.py 127.0.0.1:$port "http://cs.ucsb.edu/~dnath/local_nodes.json" > $port"_server.log" 2>&1 &
done
sleep 2
tail -f *"_server.log"

