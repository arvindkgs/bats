HOST_FA=$1
FA_USER=$2
FA_PASSWORD=$3
FILE=$4
TODIR=$5
expect -c "
        spawn scp -q -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no ${FA_USER}@$HOST_FA:$FILE $TODIR
        expect password: { send $FA_PASSWORD\r }
        set timeout 500
        expect eof
"| tr -d "\r"


