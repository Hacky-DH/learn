#!/bin/bash

# usage: gen_ssh.sh ip password

pass=
if [[ ! -z $2 ]];then
    pass=$(cat $2)
fi
cat > $1.exp <<EOF
#!/usr/bin/expect
#set timeout 20
spawn -noecho ssh root@$1 -o StrictHostKeyChecking=no
expect "*password:"
send "$pass\r"
interact
EOF

chmod +x $1.exp
echo "create $1.exp done"
