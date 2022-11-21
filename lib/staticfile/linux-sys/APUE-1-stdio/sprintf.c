#include <stdio.h>
#include <stdlib.h>

int main(void){
	char s[100];
	int year=2021, month=3, day=4;
	sprintf(s,"%d-%d-%d", year, month, day);
	printf("%s\n", s);

	//char str[] = "1234";
	//printf("%d\n", atoi(str));

	return 0;
}
