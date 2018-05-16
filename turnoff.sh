#!/bin/bash

p=$(ps aux | grep lock_pc_gnome | grep -v grep | awk '{print $2}')

if ! ping -q -c 1 -W 1 8.8.8.8 >/dev/null; then
	kill $p
 	exit 1
fi