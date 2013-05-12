#!/bin/sh
# list currrent (md5<tab>file)
MGR="../manage.py"
(echo "BEGIN; SELECT id, md5, fname FROM dasarchive_file ORDER BY id; COMMIT;") | $MGR dbshell | while read i
do
    ID=`echo $i | gawk 'BEGIN {FS="|"} {print $1}'`
    MD5=`echo $i | gawk 'BEGIN {FS="|"} {print $2}'`
    FNAME=`echo $i | gawk 'BEGIN {FS="|"} {print $3}'`
    HEXID=`printf "%08X" $ID`
    DIR=`echo $HEXID | sed 's/^\(.\{2\}\)\(.\{2\}\)\(.\{2\}\)\(.\{2\}\)/\1\/\2\/\3\/\4/'`
    echo -e "$MD5\t$DIR/$FNAME"
done
