#include "fr/fr.h"

unsigned int fr_probe(void* addr){

	unsigned int time=0;

	__asm__ volatile (
		 "mfence\n"
		"lfence\n"
		"rdtsc\n"
		"lfence\n"
		"movl %%eax, %%esi\n"
		"movl (%1), %%eax\n"
		"mfence\n"
		"lfence\n"
		"rdtsc\n"
		"lfence\n"
		"subl %%esi, %%eax\n"
		"clflush 0(%1)\n"
		: "=a"(time)
		: "c"(addr)
		: "%esi", "%edi"
	);

	return time;
}

void force_flush(void* addr){

	__asm__ volatile (
		"mfence\n"
		"lfence\n"
		"clflush 0(%0)\n"
		"lfence\n"
		:
		: "c"(addr)
		: "rax");
}

void force_access(void* addr){

        __asm__ volatile(
                        "mfence\n"
                        "lfence\n"
                        "movl (%0), %%eax\n"
                        "lfence\n"
                        :
                        : "r"(addr)
                        : "eax"
                );
}

void translate_offsets(FR* fr, void* mmap_addr){

	for( unsigned int i=0; i < fr->len; i++ )

		fr->addrs[i] = (void*)( (long)mmap_addr + (long)fr->addrs[i] );
}

typedef struct mmap_info {

	size_t size;
	void* base_addr;
} mmap_info;

void load_elf(mmap_info* mi, const char* filename){

	int fd = open(filename, O_RDONLY);

	mi->size = lseek(fd, 0, SEEK_END);

	if( mi->size & sysconf(_SC_PAGE_SIZE) ){

		mi->size |= sysconf(_SC_PAGE_SIZE);
		mi->size++;
	}

	mi->base_addr = mmap(0, mi->size, PROT_READ, MAP_SHARED, fd, 0);
	close(fd);
}

void fr_monitor_raw(FR* fr){

	// flush everything to avoid false hits in first round
	for(unsigned int i=0; i < fr->len; i++) force_flush(fr->addrs[i]);

	for(unsigned int i=0; i < fr->res_len;){

		for( unsigned int j=0; j < fr->len; j++ ){
			
			unsigned int time = fr_probe(fr->addrs[j]);

			if( fr->hit_begin <= time && time <= fr->hit_end ){

				printf("%u", j);
				fflush(stdout);
				//fr->results[i * fr->len + j] = 1;
				//i++;
			}
		}
	}
}

void fr_monitor_elf(FR* fr, const char* filename){

	mmap_info mi = (mmap_info){ 0, NULL };

	load_elf(&mi, filename);
	translate_offsets(fr, mi.base_addr);
	fr_monitor_raw(fr);

	munmap(mi.base_addr, mi.size);
}

unsigned int force_hit(void* addr){

	force_access(addr);
	return fr_probe(addr);
}

unsigned int force_miss(void* addr){

	force_flush(addr);
	return fr_probe(addr);
}

void hit_loop(double hist[][2], unsigned int n, void* addr){

	for(; n > 0; n--){

		unsigned int time = force_hit(addr);
		if( time >= HIST_SIZE ) time = HIST_SIZE - 1;
		hist[time][0]++;
	}
}

void miss_loop(double hist[][2], unsigned int n, void* addr){

	for(; n > 0; n--){
		unsigned int time = force_miss(addr);
		if( time >= HIST_SIZE ) time = HIST_SIZE - 1;
		hist[time][1]++;
	}
}

void normalize_hist(double hist[][2], unsigned num_samples){

	for( unsigned int i=0; i < HIST_SIZE; i++ ){

		hist[i][0] /= num_samples/2;
		hist[i][1] /= num_samples/2;
	}
}

double peak_heuristic(double* sample) {

	return sample[0];
}

unsigned int find_hit_peak(double hist[][2]) {

	double peak[2] = {0};

	for(unsigned int i=0; i < HIST_SIZE; i++ ){

		double heuristic = peak_heuristic(hist[i]);
		if( peak[1] < heuristic ){

			peak[0] = i;
			peak[1] = heuristic;
		}
	}

	return (unsigned int)peak[0];
}

unsigned int is_difference_enough(double* sample, double sensibility){

	return ( !sample[1] ) || ( sample[0]/( sample[0] + sample[1] ) >= sensibility );
}

unsigned int find_right_boundry(double hist[][2], unsigned int hit_peak, double sensibility){


	unsigned int i = hit_peak;
	for(; i < HIST_SIZE; i++)

		if( !is_difference_enough(hist[i], sensibility) )
			return i - (hit_peak!=i);

	return i;
}

unsigned int find_left_boundry(double hist[][2], unsigned int hit_peak, double sensibility){

	unsigned int i = hit_peak;
	for(; i > 0; i--)

		if( !is_difference_enough(hist[i], sensibility) ) return i + (hit_peak!=i);

	return i;
}

void find_hit_range(FR* fr, double hist[][2], double sensibility) {

	unsigned hit_peak = find_hit_peak(hist);

	//find boundaries
	fr->hit_begin = find_left_boundry(hist, hit_peak, sensibility);
	fr->hit_end = find_right_boundry(hist, hit_peak, sensibility);
}

void hist_to_csv(double hist[][2], const char* filename){

	if( !filename ) return;

	FILE* file = fopen(filename, "w");

	fprintf(file, "timestamp, hit_frequency, miss_frequency\n");

	for( unsigned int i = 0; i < HIST_SIZE; i++ ){

		fprintf(file, "%u, %lf, %lf", i, hist[i][0], hist[i][1]);

		if( i != HIST_SIZE - 1) fprintf(file, "\n");
	}

	fclose(file);
}

void fr_calibrate(FR* fr, double sensibility, unsigned int num_samples, const char* filename){

	// [0] - hit
	// [1] - miss
	double hist[HIST_SIZE][2]={0};
	void* test_addr = malloc(1);

	hit_loop(hist, num_samples/2, test_addr);
	miss_loop(hist, num_samples/2, test_addr);

	free(test_addr);

	normalize_hist(hist, num_samples);

	find_hit_range(fr, hist, sensibility);

	hist_to_csv(hist, filename);
}
