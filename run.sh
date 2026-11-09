#!/bin/bash
# one wake-up, with the folder and keys sorted out. this is what the timer calls.
cd "$(dirname "$0")" || exit 1
exec /usr/bin/env python3 ./tick.py "$@" >> cron.log 2>&1
