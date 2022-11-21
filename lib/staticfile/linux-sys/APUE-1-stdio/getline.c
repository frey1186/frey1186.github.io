#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char* argv[]){

	if(argc < 2){
		fprintf(stderr, "%s filename \n", argv[0]);
		exit(EXIT_FAILURE);
	}
	
	FILE *fp;
	char *linebuf;
	size_t linesize;
	
	/*非常重要*/
	linebuf = NULL;
	linesize = 0;
	
	fp = fopen(argv[1], "r");
	if(fp == NULL){
		perror("fopen()");
		exit(EXIT_FAILURE);
	}
	
	while(1){
		if (getline(&linebuf, &linesize, fp ) < 0){
			break;
		}
		printf("%ld\n", strlen(linebuf));
		printf("%ld\n", linesize);
	}

	fclose(fp);
	return 0;
}
