#!/bin/bash

#
# Download a ibm redbook or a redpaper with the Paper ID.
# 
# Created date: 2019-09-18
#


PAPER_ID=$1

HEAD_2_CHAR=$(echo $PAPER_ID|cut -b 1-2)

if [ $HEAD_2_CHAR == "re" ]; then
    PAPER_TYPE="redpapers"
elif [ $HEAD_2_CHAR == "sg" ]; then
    PAPER_TYPE="redbooks"
else
    echo "Wrong Paper ID !!!"
    exit 100
fi	
	

if [ $PAPER_TYPE ]; then
    wget "https://www.redbooks.ibm.com/$PAPER_TYPE/pdfs/$PAPER_ID.pdf"
fi
