#!/bin/bash

# 찾을 프로세스명
process_name="python3 chariot.py"

# 프로세스를 찾아서 PID를 얻음
pids=$(pgrep -f "$process_name")

# PID가 존재하는지 확인하고 프로세스를 종료
if [ -n "$pids" ]; then
    echo "프로세스를 찾았습니다. PIDs: $pids"
    
    # 모든 PID에 대해 반복하여 종료
    for pid in $pids; do
        echo "프로세스를 종료합니다. PID: $pid"
        kill "$pid"
    done
    
    echo "프로세스를 종료했습니다."
else
    echo "프로세스를 찾을 수 없습니다."
fi