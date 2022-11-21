#include <stdio.h>
#include <stdlib.h>

int main(int argc, char* argv[]){

	if(argc < 2){
		printf("Usage: %s filename\n", argv[0]);
		exit(1);
	}

	FILE* fp;
	fp = fopen(argv[1], "r");
	fseek(fp, 0, SEEK_END);
	printf("%ld\n", ftell(fp));

	fclose(fp);
	return 0;
}
