#!/usr/bin/bash
# 
# version: 0.1
# date: 2022-11-21
#
if [ $# -eq 3 ];
then
	echo "创建一个新的post文件，包含文件头..."
else
	echo "帮助："
	echo ""
	echo "$0 FileName Tags Catagories"
	echo "- FileName: 文件名，需要与post的标题一致"
	echo "- Tags: 可以多个，引号内使用空格分隔"
    echo "- Catagories: 多个，引号内使用空格分隔, public, os"
	echo ""
	exit
fi

FILENAME=$1
TAGS=$2
CATA=$3
TITLE=`basename $1|cut -f1 -d.`
WORKDIR="."
POST_FILENAME=`date "+%Y-%m-%d"`-$TITLE
DATETIME=`date "+%Y-%m-%d %H:%M"`

# copy imgs to image_dir
IMAGE_DIR=./imgs
echo -n "创建images临时目录: $IMAGE_DIR ..."
mkdir -p $IMAGE_DIR
echo "Done."

echo -n "创建文件..."
### add post titles 
echo """---
layout: post
title: $TITLE
date: $DATETIME
mdate: $DATETIME
tags: $TAGS
categories: $CATA
---""" |tee  ./$POST_FILENAME.md
echo "Done."
