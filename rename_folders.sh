#!/usr/bin/env bash
# 1. cd into the directory with all the wrong names inside
# 2. execute the script wherever it lies. execute without ./ only file path
# 3. if you want to *really* do it after inspecting the dry-run output, append "run"
testingOrRunning="echo "
if [[ "$1" == "run" ]]; then
  testingOrRunning=""
fi
find . -mindepth 1 -maxdepth 2 -type d -name 'TeBB_*' -exec bash -c 'd="{}";e=${d#*_};e=${e/-/_};'"${testingOrRunning}"' mv "$d" "$e"' \;