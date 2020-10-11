#!/bin/bash

echo "starting spy"
./spy &
SPY_PID=$!

echo "starting victim"
echo "Test Key" | gnupg-1.4.13/g10/gpg --passphrase-fd 0 -d scripts/hello.txt.gpg 2>/dev/null 1>/dev/null

wait $SPY_ID
