#!/bin/bash

# filename: Exportdata_MongoDB.sh
##
# 本程序主要用于异地备份MongoDB表数据
# 程序功能如下:
# 1.  本程序初始备份设定值为: START
# 2.  本程序执行后将默认备份: $int<=5 5张表
# 3.  本程序将备份后的文件压缩为bz2格式
# 4.  本程序在执行完文件压缩后，将删除源文件，保留压缩后文件
# 5.  本程序执行后将删除Mongodb已经备份后的数据表，释放Mongodb服务资源
# 6.  本程序执行后将压缩后的文件上传至FTP服务器
# 7.  本程序执行后将生成md5校验文件，用于文件校验
##

# see: https://www.mongodb.com/try/download/database-tools
# System_CentOS7: yum install mongodb-database-tools-rhel70-x86_64-100.3.1.rpm
# System_Ubuntu18.04: dpkg -i mongodb-database-tools-ubuntu1804-x86_64-100.3.1.deb

# see 
# System_CentOS7: yum install mongodb-org-shell-4.2.14
# System_Ubuntu18.04: dpkg -i https://downloads.mongodb.com/compass/mongodb-mongosh_0.14.0_amd64.deb

# Release compressed files 
# example: filename.tar.bz2
# yum install bzip2
# tar jxvf filename.tar.bz2 -C release/


ftpupload(){
	ftp -i -n $1 <<EOF
	user $2 $3
	passive
	put $4
EOF
}

MongoTableDrop(){
    mongosh mongodb://$1:$2/$3 -u $4 -p $5 <<EOF
	db.$6.drop()
EOF
}



# FTP_INFO
FHOST="ftp.domain.com"
FUSER="USER"
FPASS="PASS"

# MongoDB_INFO
HOST="mongodb.domain.com"
PORT="8635"
USER="USER"
PASS="PASS"
DATABASE_NAME="DATEBASENAME"
SRC_TABLE_NAME="tb_vehicle_status_his_"
TYPE="json"

START="20191101"
int=0
while (( $int<=5 ))
do
	START_T=`date -d "${START} +${int} days" "+%y_%m_%d" `
	START_TABLE_NAME=${SRC_TABLE_NAME}${START_T}
	# example: echo "${START_TABLE_NAME}": tb_vehicle_status_his_19_11_01

	# export_data
	mongoexport -h ${HOST} --port ${PORT} -u ${USER} -p ${PASS} -d ${DATABASE_NAME} -c ${START_TABLE_NAME} --type=${TYPE} -o ${START_TABLE_NAME}.${TYPE}
	sleep 10
	SIZE=`du -sh ${START_TABLE_NAME}.${TYPE} | awk '{print $1}'`
	tar jcf ${START_TABLE_NAME}.${TYPE}-${SIZE}-.bz2 ${START_TABLE_NAME}.${TYPE}

	# generate verification file
	md5sum ${START_TABLE_NAME}.${TYPE}-${SIZE}-.bz2 > ${START_TABLE_NAME}.${TYPE}-${SIZE}-.bz2.md5
	sleep 10
	
    if [ $? -eq 0 ];then
	    # DELETE START_TABLE_NAME FILE
        rm -rf ${START_TABLE_NAME}.${TYPE}
        echo "$(date '+%Y_%m_%d %H:%M:%S') Code: 200 Deleted: ${START_TABLE_NAME}.${TYPE}" >> log.txt
		
        # FTP_UPLOAD_FILE
        ftpupload ${FHOST} ${FUSER} ${FPASS} ${START_TABLE_NAME}.${TYPE}-${SIZE}-.bz2
        if [ $? -eq 0 ];then
			echo "$(date '+%Y_%m_%d %H:%M:%S') Code: 200 UPLOAD_File: ${START_TABLE_NAME}.${TYPE}-${SIZE}-.bz2" >> log.txt
            rm -rf ${START_TABLE_NAME}.${TYPE}-${SIZE}-.bz2
        fi		

		# FTP_UPLOAD_FILE_MD5
		ftpupload ${FHOST} ${FUSER} ${FPASS} ${START_TABLE_NAME}.${TYPE}-${SIZE}-.bz2.md5
        if [ $? -eq 0 ];then
			echo "$(date '+%Y_%m_%d %H:%M:%S') Code: 200 UPLOAD_File: ${START_TABLE_NAME}.${TYPE}-${SIZE}-.bz2.md5" >> log.txt
            rm -rf ${START_TABLE_NAME}.${TYPE}-${SIZE}-.bz2.md5
        fi
    fi

	# DROP_MongoDB_Table
	MongoTableDrop ${HOST} ${PORT} ${DATABASE_NAME} ${USER} ${PASS} ${START_TABLE_NAME}
	echo "$(date '+%Y_%m_%d %H:%M:%S') Code: 200 Deleted Table: ${START_TABLE_NAME}" >> log.txt

	# Clean up files to free up space
	echo "$(date '+%Y_%m_%d %H:%M:%S') Deleted MD5FILE: ${START_TABLE_NAME}.${TYPE}-${SIZE}-.bz2.md5" 
	rm -rf ${START_TABLE_NAME}.${TYPE}-${SIZE}-.bz2.md5
	let "int++"
done
