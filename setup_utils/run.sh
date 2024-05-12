#!/bin/bash

service cron start
crontab setup_utils/cront.txt
python3 vpnBot/bot/main.py