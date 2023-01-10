#!/usr/bin/env bash
testingOrRunning="echo "
if [[ "$1" == "run" ]]; then
  testingOrRunning=""
fi
find . -mindepth 1 -maxdepth 2 -type d -name 'TeBB_*' -exec bash -c 'd="{}";e=${d#*_};e=${e/-/_};'"${testingOrRunning}"' mv "$d" "$e"' \;