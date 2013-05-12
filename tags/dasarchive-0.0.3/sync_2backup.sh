#!/bin/sh
# Full sync production folder to backup
SRC=/mnt/shares/dasarchive
DST=`pwd`/backup
for i in outbox/ yesterday/ rollback/ dasarchive.db
do
    rsync -av --delete-after $SRC/$i $DST/$i
done
