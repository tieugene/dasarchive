#!/bin/sh
# Full sync backup to production
SRC=`pwd`/backup
DST=/mnt/shares/dasarchive
for i in outbox/ yesterday/ rollback/ dasarchive.db
do
    rsync -av --delete-after $SRC/$i $DST/$i
done
