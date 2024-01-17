#!/bin/bash

port=${1:-80}
# find port and inode
cat /proc/net/tcp | awk '$4=="0A"{print \
strtonum("0x"substr($2,index($2,":")+1))" "$10}' | \
while read line; do
  local_port=$(echo $line | cut -d ' ' -f 1)
  if [ $local_port -eq $port ]; then
    inode=$(echo $line | cut -d ' ' -f 2)
    # find pid by inode
    for pid in $(ls /proc | grep -E '^[0-9]+$'); do
      [ -e /proc/$pid/fd ] && ls -l /proc/$pid/fd | \
        grep socket | grep -q ${inode}
      [ $? -eq 0 ] && echo pid $pid port $local_port && break
    done
    break
  fi
done
