#!/bin/bash
kinitpath=`which kinit`
realm=$REALM
kuser=${USER}@${realm}
keytab=${HOME}/.keytab

crontime='0 */4 * * * ' 
croncmd="$kinitpath $kuser -k -t $keytab"

cronline=$crontime$croncmd

if [[ "`crontab -l`" = *kinit* ]]; then
	echo "Already present"
else
	crontab -l; echo "$cronline" | crontab -
	crontab -l
fi
