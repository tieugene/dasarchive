#!/bin/sh
# create index for yesterday
# md5 mtime size fname
pushd /mnt/shares/dasarchive/yesterday > /dev/null
ls */*/*/*/* | sort | while read i
do
    FNAME=`echo "$i"|sed -e 's/^\.\///g'`
    CRC=`md5sum -b "$i"|gawk '{print $1}'`
    #STAT=`stat -c "%Y\t%s" "$FNAME"`
    STAT=`stat -c "%s" "$FNAME"`
    echo -e "$CRC\t$STAT\t$FNAME";
done
popd > /dev/null
