#!/bin/bash

# 찾을 프로세스명
process_name="python3 chariot.py"

# 프로세스를 찾아서 PID를 얻음
pid=$(pgrep -o -f "$process_name")

# PID가 존재하는지 확인하고 프로세스를 종료
if [ -n "$pid" ]; then
    echo "프로세스를 찾았습니다. 가장 낮은 PID: $pid"
    kill "$pid"
    echo "프로세스를 종료했습니다."
else
    echo "프로세스를 찾을 수 없습니다."
fi