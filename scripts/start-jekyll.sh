#!/bin/bash

# # start httpd
# dnf -y install httpd
# systemctl enable httpd --now
# 
# # make sysroot
# mkdir /root/sysroot
# dnf -y --install-root /root/sysroot gcc g++ ruby ruby-devel ipoutes dnf
# cd /root/sysroot/; tar -zcf /var/www/html/rhel.tar.gz *
# 
# # import to docker
# docker import http://ip/rhel.tar.gz rhel:9.2
# 
# # install jekyll
# gem install jekyll tzinfo minima jekyll-feed jekyll-seo-tag
# 
# 
# 
# 
# start the container
#WORKDIR=/home/yangfl/Documents/Blogs/frey1186.github.io
if [ -z "$1" ];then
	echo Usage: $0 blog_dir
	exit
fi
WORKDIR=$(readlink -f $1)
# start docker daemon
sudo systemctl start docker
sudo docker run -it --rm --net=host --privileged=true -v ${WORKDIR}:/jekyll rhel92/jekyll:4.3.3

