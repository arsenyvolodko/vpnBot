#!/bin/bash

source venv/bin/activate
pid=`ps ax | grep python3 | grep main.py | grep -E -o ^'[0-9]+'`
kill $pid
echo '' > logs.txt
echo '' > nohub.out
nohup python3 main.py &
echo nohub.out
