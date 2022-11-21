/*
 * Copy a file from src to dist
 * use fgetc and fputc
 */
#include <stdio.h>
#include <stdlib.h>
#define BUF_SIZE 1024

int main(int argc, char* argv[]){
	
	if(argc < 3){
		fprintf(stderr, "Usage: %s src_file dist_file \n", argv[0]);
		exit(1);
	}
	
	FILE *fps,*fpd;
	char buf[BUF_SIZE];

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

	while(fread(buf, 1, 1, fps) != 0){
		fwrite(buf, 1, 1, fpd);
	}

	fclose(fpd);
	fclose(fps);

	return 0;
}
