#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

int main(int argc, char* argv[]){
	if(argc < 4){
		fprintf(stderr, "Usage:%s sfilename dfilename bufSize\n", argv[0]);
		exit(EXIT_FAILURE);
	}	

	int bufSize = atoi(argv[3]);
	int sfd, dfd;
        char buf[bufSize];
        int n, ret;
        int count = 0;

        sfd = open(argv[1], O_RDONLY);
        if(sfd < 0){
                perror("open()");
                exit(1);
        }
        dfd = open(argv[2], O_WRONLY|O_CREAT|O_TRUNC, 0600);
        if(dfd < 0){
                perror("open()");
                exit(1);
        }

        while(1){
                n = read(sfd, buf, bufSize);
                if(n<0){
                        perror("read()");
                        break;
                }
                if(n==0){break;}
                ret = write(dfd, buf, n);
                count++;
        }

        close(dfd);
        close(sfd);
	
	printf("%10d %10d ", bufSize, count);
	return 0;
}
