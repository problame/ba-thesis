#!/bin/bash
set -e

if [ "$#" -lt 2 ]; then
    echo "usage: $(basename $0) IMAGE CORE_RANGE [QEMU_ARGS...]"
	exit 1
fi

image="$1"
shift
core_range="$1"
shift

cores=$(seq -s ' ' $(echo "$core_range" | tr '-' ' '))
core_map=""
core_count=0
for c in $cores; do
    core_map="$core_map $core_count:$c";
    core_count=$(( core_count + 1 ))
done

tmpfsimg=/tmp/linuxvm.img
cp "$image" "$tmpfsimg"

qemu-system-x86_64 -name linuxvm,debug-threads=on -smp "${core_count}" -hda "${tmpfsimg}" -boot c -net bridge,br='eval' -net nic,model=virtio,name=eval_linuxvm -m 2G -localtime -enable-kvm -display none -serial stdio&
qemu_pid=$!
echo "spawned qemu_pid=${qemu_pid}"
trap "kill ${qemu_pid}; exit" INT TERM
sleep 2
cd "$(dirname $0)"
python3 qemu-affinity/qemu_affinity.py  -v -k ${core_map} -- ${qemu_pid}
echo "affinity set, waiting for qemu to terminate"
wait "${qemu_pid}"
echo "qemu terminated"
exit 0
