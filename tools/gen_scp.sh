#!/bin/bash

# usage: gen_scp.sh ip password

pass=
if [[ ! -z $2 ]];then
    #password may has ctrl char
    pass=$(cat $2)
fi
cat > s$1.exp <<EOF
#!/usr/bin/expect -f
set files [lindex \$argv 0]
set timeout 30
spawn -noecho scp -o StrictHostKeyChecking=no -r \$files root@$1:/root/
expect "*password:"
send "$pass\r"
interact
EOF

chmod +x s$1.exp
echo "create s$1.exp done"
