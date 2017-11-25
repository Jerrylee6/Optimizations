#!/bin/bash
#
# chkconfig: - 90 10
# description:      Optimizing server performance
#                   System:     CentOS 6 x64
#                   Version:    1.0
#
# @name:            Linux system optimization.sh
# @author:          51inte <51inte@hotmail.com>
# @created:         13.3.2017
# @Script Version:  v1.0
#
#
# Source function library.
. /etc/init.d/functions

# Variables

usage(){
case $choice in
	1)
		sed -i '/^SELINUX/s/enforcing/disabled/g' /etc/selinux/config
		setenforce 0
	;;
	2)
		sed -i "/ACTIVE_CONSOLES=\/dev\/tty/s/6/3/g" /etc/init/start-ttys.conf
		sed -i "/^ACTIVE_CONSOLES=\/dev\/tty/s/6/3/g" /etc/sysconfig/init
		## need reboot ## ##netstat -nat |grep tty
	;;
	3)
		sed -i '/exec/s/^/#/g' /etc/init/control-alt-delete.conf
	;;
	4)
		
	;;
	5)
		yum install ntp
		echo "0 0 * * *    /usr/sbin/ntpdate 0.centos.pool.ntp.org" >> /etc/crontab
		/etc/init.d/crond reload
	;;
	6)
		sed -i "/^*/s/1024/65535/" /etc/security/limits.d/90-nproc.conf
		echo "Permanently need to restart the system. If temporary action is needed, \" ulimit -SHn 65535 \" will be executed"
	;;
	7)
		echo "net.ipv4.tcp_max_tw_buckets = 6000" >>/etc/sysctl.conf
		echo "net.ipv4.ip_local_port_range = 1024 65000" >>/etc/sysctl.conf
		echo "net.ipv4.tcp_tw_recycle = 1" >>/etc/sysctl.conf
		echo "net.ipv4.tcp_tw_reuse = 1" >>/etc/sysctl.conf
		echo "net.ipv4.tcp_syncookies = 1" >>/etc/sysctl.conf
		
		echo "net.core.somaxconn = 262144" >>/etc/sysctl.conf
		echo "net.core.netdev_max_backlog = 262144" >>/etc/sysctl.conf
		
		echo "net.ipv4.tcp_max_orphans = 262144" >>/etc/sysctl.conf
		echo "net.ipv4.tcp_max_syn_backlog =262144" >>/etc/sysctl.conf
		echo "net.ipv4.tcp_synack_retries = 1" >>/etc/sysctl.conf
		echo "net.ipv4.tcp_syn_retries = 1" >>/etc/sysctl.conf
		echo "net.ipv4.tcp_fin_timeout = 1" >>/etc/sysctl.conf
		echo "net.ipv4.tcp_keepalive_time = 30" >>/etc/sysctl.conf
		/sbin/sysctl -p
	;;
	Q)
		exit 0;
	;;
esac
}

while :
do

cat <<EOF
=======================================
1.............................Disabled selinux
2.............................Change the TTY changed from 6 to 3
3.............................Disabled control-alt-delete
4.............................Disabled Print_Service
5.............................Time synchronization
6.............................Maximum number of open files
7.............................Optimize Kernel
8.............................Optimize CPU/IO
Q.............................exit
=======================================
EOF

	read -p "Please Enter Your Choice:" choice
	usage

done