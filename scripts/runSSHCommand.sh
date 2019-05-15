HOST_FA=$1
FA_USER=$2
FA_PASSWORD=$3
COMMAND=$4
expect -c "
        spawn ssh -q -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no ${FA_USER}@$HOST_FA $COMMAND
        expect password: { send $FA_PASSWORD\r }
        set timeout 500
        expect eof
"| tr -d "\r"


