#!/usr/bin/env bash
# 1. cd into the directory with all the wrong names inside
# 2. execute the script wherever it lies. execute without ./ only file path
#    ~w/Code/process_gc_ms_data/rename_folders.sh
# 3. if you want to *really* do it after inspecting the dry-run output, append "-run"
#    ~w/Code/process_gc_ms_data/rename_folders.sh run
testingOrRunning="echo "
if [[ "$1" == "run" ]]; then
  testingOrRunning=""
fi
#Find every folder name starting with TeBB, replace with nothing
#find . -mindepth 1 -maxdepth 2 -type d -name 'TeBB_*' -exec bash -c 'd="{}";e=${d#*_};e=${e/-/_};'"${testingOrRunning}"' mv "$d" "$e"' \;

#Find every folder name ending with _80.D or _20.D and delete the ending, add E20 or E80 to the start
#find . -mindepth 1 -maxdepth 1 -type d -name '*_80.D' -exec bash -c 'd="{}";e="${d%_*}.D";e="./E80_${e#*/}";'"${testingOrRunning}"' mv "$d" "$e"' \;

#Find every folder name beginning with D20_ and replace it with D2O
find . -mindepth 1 -maxdepth 2 -type d -name 'D20_*' -exec bash -c 'd="{}";e=${d#*_};e="./D2O_${e#*/}";'"${testingOrRunning}"' mv "$d" "$e"' \;

