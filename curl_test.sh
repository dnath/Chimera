#!/bin/bash

URL=http://localhost:5000

ROUTE=$1
shift
PARAMS=$@

case $ROUTE in
	/)
		curl $URL
		;;
	/message)
		param_string=''
		for param in $PARAMS; do param_string+="-d $param "; done
		curl $URL/message $param_string
esac
