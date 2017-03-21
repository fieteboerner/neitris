#! /bin/bash

echo "Starting Neitris Server and Client"
/usr/bin/python2 neitris_server.py > /dev/null &
pid=$!
/usr/bin/python2 neitris.py 127.0.0.1 ; kill -9 $pid
