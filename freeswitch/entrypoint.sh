#!/bin/sh
set -eu
ip=${LAB_PUBLIC_IP:-127.0.0.1}
# Do not allow configuration injection via template replacement.
case "$ip" in ''|*[!0-9.]*) echo 'LAB_PUBLIC_IP must be an IPv4 address' >&2; exit 1;; esac
awk -v ip="$ip" 'BEGIN { n=split(ip,a,"."); if(n!=4) exit 1; for(i=1;i<=4;i++) if(a[i]=="" || a[i]+0>255) exit 1 }' || exit 1
sed "s/__LAB_PUBLIC_IP__/$ip/g" /etc/freeswitch/freeswitch.xml.template > /etc/freeswitch/freeswitch.xml
exec "$@"
