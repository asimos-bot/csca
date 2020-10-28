#!/bin/bash

function get_statistics(){

	./spy &
	SPY_PID=$!

	gnupg-1.4.13/g10/gpg --passphrase "Test Key" --armor -q -d scripts/hello.txt.gpg

	wait $SPY_PID

	grep ",1" spy.csv >/dev/null
	GREP_EXIT_CODE=$?
	if [[ $GREP_EXIT_CODE -eq 0 ]];
	then
		echo "Sucess! (hits detected)"
	else
		echo "Error! (no hits)"
		exit
	fi

	scripts/bits.py spy.csv
}

rm -f scripts/bits.csv

for i in {1..100}
do
	get_statistics
done
