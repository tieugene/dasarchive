#!/bin/sh
# Full sync current to yesterday
ROOT=/mnt/shares/dasarchive
rsync -av --delete-after $ROOT/outbox/00/ $ROOT/yesterday/00/
bin/test0.sh > $ROOT/yesterday/index.txt
