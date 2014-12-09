#!/usr/bin/env bash

echo 'Killing previously running servers, if any...'
kill -9 $(ps aux | grep 'chimera-api/env/bin/python ./server.py' | awk '{print $2}')
