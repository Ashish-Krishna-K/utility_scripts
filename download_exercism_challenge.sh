#!/bin/bash

echo "Enter the download command: "
read command
output=$(eval "$command")
file=$(echo "$output" | tail -n 1)
code "$file"
