/*
 * Copy a file from src to dist
 * use fgetc and fputc
 */
#include <stdio.h>
#include <stdlib.h>
#define BUFSIZE 1024


int main(int argc, char* argv[]){
	
	if(argc < 3){
		fprintf(stderr, "Usage: %s src_file dist_file \n", argv[0]);
		exit(1);
	}
	
	FILE *fps,*fpd;
	char buf[BUFSIZE];

	fps = fopen(argv[1], "r");  // 必须存在
	if(fps == NULL){
		perror("fopen srcFile");
		exit(1);
	}
	fpd = fopen(argv[2], "w");
	if(fpd == NULL){
		perror("fopen distFile");
		fclose(fps);
		exit(1);
	}

	while(fgets(buf, BUFSIZE, fps) != NULL){
		fputs(buf, fpd);
	}


	fclose(fpd);
	fclose(fps);

	return 0;
}
