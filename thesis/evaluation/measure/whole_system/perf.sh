#!/bin/bash

if [ "$OUTDIR" == "" ]; then
    echo "OUTDIR must be set"
    exit 1
fi

if [ "$#" != 3 ]; then
    echo "usage: $(basename $0) EVENTS MODIFIERS CORES"
    exit 1
fi


EVENTS="$1"
MODS="$2"
CORES="$3"

function join_by { local IFS="$1"; shift; echo "$*"; }

EVENT_PARAM=""
for e in $EVENTS; do
    EVENT_PARAM="${EVENT_PARAM},${e}:${MODS}"
done

exec perf stat -e "$EVENT_PARAM" -C "$CORES" -o "$OUTDIR/perf.out" -x ';'
