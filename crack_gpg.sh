#!/bin/bash

function get_statistics(){

	rm -f scripts/hello.txt.gpg
	./spy &
	SPY_PID=$!

	gnupg-1.4.13/g10/gpg --yes --local-user AFDE2AAC --sign scripts/hello.txt

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

for i in {1..20}
do
	get_statistics
done
