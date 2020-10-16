#!/bin/bash

./spy > spy.log &
sleep 2

gnupg-1.4.13/g10/gpg --passphrase "Test Key" --armor -q -d scripts/hello.txt.gpg
