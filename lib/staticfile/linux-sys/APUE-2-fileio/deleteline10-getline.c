#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>


#define LINE 10

int main(int argc, char* argv[]){
	
	if(argc < 2){
		fprintf(stderr, "Usage: %s filename \n", argv[0]);
		exit(1);
	}	

	FILE *fp1, *fp2;	
	char * line = NULL;
        size_t len = 0;
        ssize_t read;
	long start_w, start_r;
	int lines = 0;
	char buf[1];
	off_t length = 0;

	fp1 = fopen(argv[1], "r");
	if(fp1 == NULL){
		perror("fp1 open()");
		exit(1);
	}
	
	fp2 = fopen(argv[1], "r+");
	if(fp2 == NULL){
		perror("fp2 open()");
		exit(1);
	}

	while ((read = getline(&line, &len, fp1)) != -1) {
	       	lines++;
               	//printf("Retrieved line of length %zu :\n", read);
               	//printf("%s", line);
		if(lines == LINE-1) start_w = ftell(fp1);
		if(lines == LINE) {
			start_r = ftell(fp1);
			break;
		}
           }		
	printf("start_r = %ld, start_w = %ld \n", start_r, start_w);
	
	fseek(fp2, start_w, SEEK_SET);
	fseek(fp1, start_r, SEEK_SET);
	length = start_r;
	while(1){
		if(fread(buf, 1, 1, fp1) < 1) break;
		fwrite(buf, 1, 1, fp2);
		length++;
	}

	fclose(fp2);
	fclose(fp1);

	if(truncate(argv[1], length) < 0){
		perror("truncate()");
		exit(1);
	}
	return 0;
}
