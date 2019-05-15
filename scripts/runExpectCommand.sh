#!/usr/bin/expect -f

spawn ssh $1@$2
expect "password" { send "$3\r"}
expect "#"; # This '#' is nothing but the terminal prompt
send "$4\r"
expect "#"
puts $expect_out(buffer);  #Will print the output of the 'cmd' output now.
