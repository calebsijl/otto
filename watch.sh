#!/bin/bash
# Start otto living in real time, and the console to watch him in.
cd "$(dirname "$0")" || exit 1

if [ ! -f .env ]; then echo "no .env — put your api key in it first."; exit 1; fi

# the server, if it is not already up
if ! curl -s -o /dev/null http://localhost:8080/api/feed 2>/dev/null; then
  python3 serve.py > serve.log 2>&1 &
  sleep 1
  echo "server started"
fi

echo
echo "  console   http://localhost:8080          (the 'now' tab is the live one)"
echo "  the lane  http://localhost:8080/world.html"
echo
echo "he wakes every 20 minutes. ctrl-c stops him; the server keeps running."
echo "----------------------------------------------------------------------"
while true; do
  python3 tick.py --realtime
  sleep 1200
done
