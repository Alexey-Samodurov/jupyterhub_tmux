#!/usr/bin/env bash

if [[ $1 == 'start' ]]; then
  python3 ./start.py --sessions_num "$2"
elif [[ $1 == 'stop' ]]; then
  python3 ./stop.py --session_name "$2"
elif [[ $1 = 'stop_all' ]]; then
  python3 ./stop_all.py
else
  echo "main.sh can get only start, stop or stop_all arguments. Please check your args names"
  exit 1
fi