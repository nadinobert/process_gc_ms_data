#!/usr/bin/env bash
# 1. cd into the directory with all the wrong names inside
# 2. execute the script wherever it lies. execute without ./ only file path
#    ~w/Code/process_gc_ms_data/rename_folders.sh
# 3. if you want to *really* do it after inspecting the dry-run output, append "run"
testingOrRunning="echo "
if [[ "$1" == "run" ]]; then
  testingOrRunning=""
fi
#find . -mindepth 1 -maxdepth 2 -type d -name 'TeBB_*' -exec bash -c 'd="{}";e=${d#*_};e=${e/-/_};'"${testingOrRunning}"' mv "$d" "$e"' \;

# replace the last character of folder name -> replace 3 by 6
#find . -mindepth 1 -maxdepth 2 -type d -name '*3.D' -exec bash -c 'd="{}";e=${d%3}6;'"${testingOrRunning}"' mv "$d" "$e"' \;

# replace the first character of folder name -> replace E by D2O
find . -mindepth 1 -maxdepth 2 -type d -name 'E*' -exec bash -c 'd="{}";e=${d:0:2}"D2O"${d:3};'"${testingOrRunning}"' mv "$d" "$e"' \;