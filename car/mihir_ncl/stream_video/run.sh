#!/bin/bash
# starts the car camera + mjpeg stream, prints the link to open on the mac
# ctrl+c to stop everything
cd "$(dirname "$0")"
source /opt/ros/humble/setup.bash
source ~/LearningAdaptive/install/setup.bash

ros2 launch rover_hardware camera.launch.py > camera.log 2>&1 &
CAM=$!
stop() {
  trap '' INT TERM   # only run this once
  echo "stopping..."
  kill -INT $CAM 2>/dev/null; sleep 3
  pkill -f "camera_driver_node|image_transport/republish|topic_tools/relay" 2>/dev/null
  echo "stopped"
  exit
}
trap stop INT TERM

echo "starting camera (log in camera.log)..."
for i in $(seq 30); do
  ros2 topic list 2>/dev/null | grep -q /color/image/compressed && break
  sleep 1
done

# ip to open from the laptop (the one you ssh'd in on, else wifi)
IP=$(echo $SSH_CONNECTION | awk '{print $3}')
[ -z "$IP" ] && IP=$(ip -4 -o addr show wlan0 | awk '{print $4}' | cut -d/ -f1)
echo ""
echo "open on mac:  http://$IP:8080"
echo ""
python3 stream.py
stop
