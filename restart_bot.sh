#!/bin/bash

source venv/bin/activate
pid=`ps ax | grep python3 | grep main.py | grep -E -o ^'[0-9]+'`
kill $pid
echo '' > logs.txt
echo '' > nohup.out
nohup python3 main.py &
cat nohup.out
