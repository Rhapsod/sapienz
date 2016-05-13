#!/bin/bash

kill -9  $(ps aux | grep 'emulator' | awk '{print $2}')
kill -9  $(ps aux | grep 'adb' | awk '{print $2}')
adb start-server
rm /home/kemao/tmp/android-kemao/*
kill -9 $(lsof -i:23745 | tail -n +2 | awk '{print $2}') 

