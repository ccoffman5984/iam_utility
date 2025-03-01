#!/bin/bash

# The account targets are stored in a text file

if [ -z "$1" ]; then
  echo "Usage: process_listing.sh <account_list_file>"
  exit 1
fi

account_list_file=$1

# loop through the account targets and invoke python to disable access keys

while IFS= read -r account_number
do

  echo "processing $account_number"
  command="python disable_access_keys $account_number"
  echo "command: $command"
  $command
  

done < "$account_list_file"