#!/usr/bin/bash
# 
# version: 0.1
# date: 2022-04-08
#
if [ $# -eq 3 ];
then
	echo "开始转换..."
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

echo "文章标记如下："
echo """---
layout: post
title: $TITLE
date: $DATETIME
tags: $TAGS
categories: $CATA
---"""

# copy imgs to image_dir
IMAGE_DIR=./images/$POST_FILENAME
mkdir -p $IMAGE_DIR
for imgname in `grep -E '^\!\[.*\](.*)' $FILENAME |cut -d '(' -f2|cut -d ')' -f1`
do
	echo copy  `dirname $FILENAME`/$imgname  to  $IMAGE_DIR/
	cp `dirname $FILENAME`/$imgname $IMAGE_DIR/ || exit
done

echo -n "生成文件...."
### add post titles 
echo """---
layout: post
title: $TITLE
date: $DATETIME
tags: $TAGS
categories: $CATA
---""" > ./_posts/$POST_FILENAME.md

## 替换图片目录
## 不能替换 ![](123.png)
## 需要![](./123.png)全路径
sed -e "s#^\!.*([^)]*/\(.*\))#\![](/images/$POST_FILENAME/\1)#g" $FILENAME >> ./_posts/$POST_FILENAME.md \
&& echo "Done." || exit

echo -n "Use Git add and commit..."
#git add ./_posts/$POST_FILENAME.md \
#&& git add $IMAGE_DIR \
#&& git commit -m "Add file:$POST_FILENAME and some images."
#echo "Done"
echo ""

echo "Use 'git push' to push to origin master."
