#!/bin/bash
set -e

if [ "$#" -lt 3 ]; then
    echo "usage: $(basename $0) IMAGE CORE_RANGE OSV_SUPPL_CMDLINE [OSV_RUN_SCRIPT_ARGS...]"
	exit 1
fi

image="$1"
shift
core_range="$1"
shift
osvsuppl="$1"
shift

cores=$(seq -s ' ' $(echo "$core_range" | tr '-' ' '))
core_map=""
core_count=0
for c in $cores; do
    core_map="$core_map $core_count:$c";
    core_count=$(( core_count + 1 ))
done

tmpfsimg=/tmp/dbench_osv_img.img
cp "$image" "$tmpfsimg"

osv="--ip=eth0,10.23.42.10,255.255.255.0 --defaultgw=10.23.42.35 --nameserver=10.23.42.35 $osvsuppl -- /usr/bin/mysqld --basedir /usr --datadir data --user root"

# must run from osv dir
cd /home/cschwarz/osv
exec scripts/run.py --bridge 'eval' -n -c ${core_count} -V --qemu-affinity-args " -v -k ${core_map}" -e " $osv" -i "$tmpfsimg" $@
#exec taskset -c "${core_range}" scripts/run.py --bridge 'eval' -n -c ${core_count} -V --qemu-affinity-args " -v -w ${core_range} -k ${core_map}" -e " $osv" -i "$tmpfsimg"
