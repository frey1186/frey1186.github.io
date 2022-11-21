#include <stdio.h>
#include <stdlib.h>

int main(void){

	//printf("Before while\n");
	printf("Before while"); //行缓存，如果不加\n，不会打印
	fflush(stdout); //必须用这个



	printf("BUFSIZ = %d \n", BUFSIZ);






	while(1);
	printf("After while\n");

	return 0;
}
