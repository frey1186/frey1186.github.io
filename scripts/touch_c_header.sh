#!/bin/bash
#
# touch a C header file ,with #ifndef xxxx
# version: 0.2
# date: 2023-8-8
#

help(){
	echo "Usage: $(basename $0) header.h"
	exit 1
}

if [ ! $1 ];then help;fi

FILE=$1

# 头文件标记，比如 __HEADER_H_
BASE=$(basename $FILE .h)
BASE_UP=$(echo ${BASE^^})
HEADER_STYLE="__${BASE_UP}_H_"

# 后缀名
EXT=${FILE#*.}

# 临时文件
TMP=$(mktemp)

[[ ${EXT} == "h" ]] || help

echo "#ifndef ${HEADER_STYLE}
#define ${HEADER_STYLE}" > ${TMP}
if [ -f $FILE ] ;then
	head -n 1 $FILE 2>/dev/null \
		| grep "#ifndef" >/dev/null 2>&1 \
		&& exit 0 ||cat $FILE >> ${TMP};
fi
touch $FILE
echo >> ${TMP}
echo "#endif // ${HEADER_STYLE}" >> ${TMP}
mv ${TMP} $FILE;

# clear the tmp file
if [ -f ${TMP} ]; then
	rm -f ${TMP}
fi
