#!/usr/bin/env bash

# directory to iterate through
dir="/mnt/c/Users/hellmold/Nextcloud/Experiments/Activity_Assay_GC_MS/20220907_TBP_Auswertung_4"

# string to add to folder names
add_string="H2O_"

# loop through all folders in the directory
for folder in "$dir"/*/
do
  # get the current folder name
  name=$(basename "$folder")
  # create the new folder named by adding the string to the end
  new_name="H2O_$name$"
  # rename the folder
  mv "$folder" "$dir/$new_name"
done
