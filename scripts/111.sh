#!/usr/bin/bash
# 
# version: 0.1
# date: 2022-11-22
#

##
DIR=$(dirname "${BASH_SOURCE[0]}")
DIR=$(realpath "${DIR}")
WORKDIR=$(dirname "${DIR}")

if [ $# -eq 1 ];
then
	echo ""
else
	echo "帮助：剪切文件到post目录，并替换图片目录"
	echo "$0 FileName"
	echo "- FileName: 文件名"
	echo ""
	exit
fi

FILENAME=$1
TAGS=$2
CATA=$3
TITLE=`basename $1|cut -f1 -d.`
POST_FILENAME=$TITLE
DATETIME=`date "+%Y-%m-%d %H:%M"`

# copy imgs to image_dir
IMAGE_DIR=${WORKDIR}/images/$POST_FILENAME
mkdir -p $IMAGE_DIR
for imgname in `grep -E '^\!\[.*\](.*)' $FILENAME |cut -d '(' -f2|cut -d ')' -f1`
do
	# echo mv $WORKDIR/$imgname  to  $IMAGE_DIR/
	mv $WORKDIR/$imgname $IMAGE_DIR/ || exit
done

##  替换图片目录
## 不能替换 ![](123.png)
## 需要![](./123.png)全路径
sed -i "s#^\!.*([^)]*/\(.*\))#\![](/images/$POST_FILENAME/\1)#g" $FILENAME \
|| exit
# 
# 剪切到_post
# mv $FILENAME $WORKDIR/_posts/

echo "$FILENAME Done."

# echo -n "Use Git add and commit..."
# #git add ./_posts/$POST_FILENAME.md \
# #&& git add $IMAGE_DIR \
# #&& git commit -m "Add file:$POST_FILENAME and some images."
# #echo "Done"
# echo ""
# 
# echo "Use 'git push' to push to origin master."
