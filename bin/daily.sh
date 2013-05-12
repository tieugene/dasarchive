#!/bin/sh
# Process backuping
MGR="../manage.py"

stage0(){
    echo "Stage 0: Prepare variables"
    pushd ../dasarchive > /dev/null
    OUTBOX_ROOT=`python -c "import settings; print settings.OUTBOX_ROOT;"`
    YESTERDAY_ROOT=`python -c "import settings; print settings.YESTERDAY_ROOT;"`
    ROLLBACK_ROOT=`python -c "import settings; print settings.ROLLBACK_ROOT;"`
    ROLLBACK_COUNT=`python -c "import settings; print settings.ROLLBACK_COUNT;"`
    popd > /dev/null
}

stage1(){
    echo "Stage 1: Prepare data"
    # 1. Yesterday
    declare -A YESTERDAY
    cat $YESTERDAY_ROOT/index.txt | while read $i
    do
        MD5=`gawk 'BEGIN {FS="\t"} {print $1}'`
        FPATH=`gawk 'BEGIN {FS="\t"} {print $1}'`
        DIR=`dirname "$FPATH"`
        YESTERDAY[$DIR]=$i
    done
    # 2. current
    declare -A CURRENT
    (echo "BEGIN; SELECT id, md5, fname FROM dasarchive_file ORDER BY id; COMMIT;") | $MGR dbshell | while read i
    do
        ID=`echo $i | gawk 'BEGIN {FS="|"} {print $1}'`
        MD5=`echo $i | gawk 'BEGIN {FS="|"} {print $2}'`
        FNAME=`echo $i | gawk 'BEGIN {FS="|"} {print $3}'`
        HEXID=`printf "%08X" $ID`
        DIR=`echo $HEXID | sed 's/^\(.\{2\}\)\(.\{2\}\)\(.\{2\}\)\(.\{2\}\)/\1\/\2\/\3\/\4/'`
        CURRENT[$DIR]="$MD5\t$DIR/$FNAME"
    done
}
stage2(){
    echo "Stage 2: Backup"
}
stage3(){
    echo "Stage 3: Clean Yesterday"
}
stage4(){
    echo "Stage 4: Clean Rollback"
}
stage5(){
    echo "Stage 5: Backup DB"
}
stage0
stage1
stage2
stage3
stage4
stage5
exit 0
