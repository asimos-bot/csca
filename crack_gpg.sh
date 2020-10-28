#!/bin/bash

function get_statistics(){

	./spy &
	SPY_PID=$!

	gnupg-1.4.13/g10/gpg --passphrase "Test Key" --armor -q -d scripts/hello.txt.gpg

	wait $SPY_PID

	grep ",1" spy.log >/dev/null
	GREP_EXIT_CODE=$?
	if [[ $GREP_EXIT_CODE -eq 0 ]];
	then
		echo "Sucess! (hits detected)"
	else
		echo "Error! (no hits)"
		exit
	fi

	scripts/crack.py spy.log | cut -f 2 -d ' ' | tr "\n" "," | grep -Eo "[\.[:alnum:]]*(,[\.[:alnum:]]*){3}" >> scripts/crack.log
}

echo "bit_1,bit_no_repetition_1,hamming_distance,levensthein" > scripts/crack.log

for i in {1..10}
do
	get_statistics
done
