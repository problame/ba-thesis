#!/bin/bash

if [ $(id -u) -ne 0 ]; then
    echo "must run as root"
    exit 1
fi

set -e

cd $(dirname "$0")

lshw > lshw.txt
cat /proc/cpuinfo > proc_cpuinfo.txt
dmidecode -t memory  > dmidecode_t_memory.txt
dmidecode -t system > dmidecode_t_system.txt

