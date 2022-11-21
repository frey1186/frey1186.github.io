#!/bin/bash

WORKDIR=/usr/local/bin/myssh_file
DATAFILE=$WORKDIR/myssh.data
EXPFILE=$WORKDIR/myssh.exp

function echo_help {
echo ""
echo "Usage: $0"
echo "             -l           List the host in datafile."
echo "             -h hostname  Connect the host with hostname."
echo "             -n lineID    Connect the host list with line id."
echo "             -e           Edit the datafile with vi."
echo "             -s           Connect a new host do not in datafile"
echo "             -a           Add a host to datafile."
echo "             -A h:u:p:d   Add a host strings to datafile."
echo ""
}


if [ ! $1 ] 
then
	echo_help
	exit
fi

if [ $1 == '-l' ]
then
	echo -e "No\tHostname\tUser\tDescriptions..."
	grep -vE "^#|^$" $DATAFILE| awk 'BEGIN{FS=":";OFS="\t"} {print NR,$1,substr($2,1,7),$4}'
	exit
fi

if [ $1 == '-h' ]
then
	host_line=`grep $2 $DATAFILE`
	HOSTNAME=`echo $host_line|awk 'BEGIN{FS=":"} {print $1}'`
	USERNAME=`echo $host_line|awk 'BEGIN{FS=":"} {print $2}'`
	PASSWORD=`echo $host_line|awk 'BEGIN{FS=":"} {print $3}'`
	$EXPFILE $HOSTNAME $USERNAME $PASSWORD
	exit
fi

if [[ $1 == '-n' && $2 -gt 0 ]]
then
	host_line=`grep -vE "^#|^$" $DATAFILE| awk 'BEGIN{FS=":";OFS=" "} {print NR,$1,$2,$3}'|grep "^$2"`
	HOSTNAME=`echo $host_line|awk '{print $2}'`
	USERNAME=`echo $host_line|awk '{print $3}'`
	PASSWORD=`echo $host_line|awk '{print $4}'`
	$EXPFILE $HOSTNAME $USERNAME $PASSWORD
	exit
fi


if [ $1 == '-e' ]
then
	vim $DATAFILE
	exit
fi

if [ $1 == '-s' ]
then
	# delete $1 
	shift 1; ssh $@
	exit
fi

if [ $1 == '-a' ]
then
	echo -n "Hostname or IP: "
	read HOSTNAME
	echo -n "Username: "
	read USERNAME
	echo -n "Password: "
	read -s PASSWORD
	echo ""
	echo -n "Description:"
	read DESC
	echo "$HOSTNAME:$USERNAME:$PASSWORD:$DESC" >> $DATAFILE
	exit
fi

if [[ $1 == '-A' && `echo $2|awk -F":" '{ print NF-1}'` == 3 ]]
then
	echo $2 >> $DATAFILE
	exit
fi

echo_help
