killall -9 $(ps aux | grep "python" | awk '{print $2}')
killall -9 $(ps aux | grep "motifcore" | awk '{print $2}')
killall -9 $(lsof -i:5037 | tail -n +2 | awk '{print $2}')
