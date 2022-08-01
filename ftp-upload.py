#!/usr/bin/python
# encoding=utf-8

'''
项目需求: 指定目录上传至FTP-Server服务器
程序功能: 整个目录上传

bug info:
1.  目前不支持单个文件上传失败，单文件续传功能
'''
import datetime
import os.path
import sys
import os
from ftplib import FTP

today = datetime.date.today()
today = today.strftime("%Y-%m-%d")  # <type 'str'>

now = datetime.datetime.now()
now = now.strftime("%H:%M:%S")  # <type 'str'>
curr_time = "[%s %s]" % (today , now)
fname = "%s.txt" % today

class MyFTP(object):
    """
    @ note: upload local file or dirs recursively to ftp server
    """

    def __init__(self):
        self.ftp = None

    def __del__(self):
        pass

    def WriteSeek(self, value):
        log_dir_str = "log"
        if not os.path.isdir(log_dir_str):
            os.mkdir(log_dir_str)  # 创建目录名为: "log"
            os.chdir(log_dir_str)  # 切换目录log
            f = open(fname , "a")
            f.write(value)
            f.write("\n")  # 换行
            f.close()
        else:
            os.chdir(log_dir_str)
            f = open(fname , "a")
            f.write(value)
            f.write("\n")  # 换行
            f.close()
        os.chdir(os.path.abspath(os.path.join(os.getcwd() , "..")))     # 切换上级目录



    def SetFTPParams(self, FTP_Server, FTP_Port, Timeout=60):
        self.FTP_Server = FTP_Server
        self.FTP_Port = FTP_Port
        self.Timeout = Timeout

    def Login(self, FTP_USER, FTP_PWD):              # FTP 初始化登录
        #########
        today = datetime.date.today()
        today = today.strftime("%Y-%m-%d")  # <type 'str'>

        now = datetime.datetime.now()
        now = now.strftime("%H:%M:%S")  # <type 'str'>
        curr_time = "[%s %s]" % (today , now)
        #########

        if self.ftp is None:
            self.ftp = FTP()
            # print '### Connect FTP Server: %s ...' % self.FTP_Server            # debug info: print

            ConnMsg = "%s Connect FTP Server: %s ..." % (curr_time, self.FTP_Server)
            self.WriteSeek( ConnMsg )                                             # write log

            self.ftp.connect(self.FTP_Server, self.FTP_Port, self.Timeout)          # 连接FTP Server
            self.ftp.login(FTP_USER, FTP_PWD)                                       # 登录FTP Server
            # print "### %s" % self.ftp.getwelcome()                              # debug info: print

    def Logout(self):

        #########
        today = datetime.date.today()
        today = today.strftime("%Y-%m-%d")  # <type 'str'>

        now = datetime.datetime.now()
        now = now.strftime("%H:%M:%S")  # <type 'str'>
        curr_time = "[%s %s]" % (today , now)
        #########
        if self.ftp:
            self.ftp.close()
            # print "### Disconnect FTP Server: %s" % self.FTP_Server                       # debug info: print

            CloseMsg = "%s Disconnect FTP Server: %s" % (curr_time, self.FTP_Server)
            self.WriteSeek( CloseMsg )                                                       # write log
            self.ftp = None

    def is_same_size(self, FTP_Local_FILE,  FTP_Remote_FILE):
        """
        note: 判断远程文件和本地文件大小是否一致
        :param FTP_Local_FILE:
        :param FTP_Remote_FILE:
        :return:
        """
        #########
        today = datetime.date.today()
        today = today.strftime("%Y-%m-%d")  # <type 'str'>

        now = datetime.datetime.now()
        now = now.strftime("%H:%M:%S")  # <type 'str'>
        curr_time = "[%s %s]" % (today , now)
        #########
        try:
            remote_file_size = self.ftp.size(FTP_Remote_FILE)
        except Exception as err:
            # self.debug_print("is_same_size() 错误描述为：%s" % err)
            remote_file_size = -1

        try:
            local_file_size = os.path.getsize(FTP_Local_FILE)
        except Exception as err:
            # self.debug_print("is_same_size() 错误描述为：%s" % err)
            local_file_size = -1

        # print ('%s Local File: %s Size: %d -- Remote File: %s Size: %d' % (curr_time, FTP_Local_FILE, local_file_size, FTP_Remote_FILE, remote_file_size))
        if remote_file_size == local_file_size:
            return 1
        else:
            return 0


    def upload_file(self, FTP_Local_FILE, FTP_Remote_FILE):
        """
        note: Upload file function
        :param FTP_Local_FILE: local file
        :param FTP_Remote_FILE: ftp server file
        :return:
        """
        #########
        today = datetime.date.today()
        today = today.strftime("%Y-%m-%d")  # <type 'str'>

        now = datetime.datetime.now()
        now = now.strftime("%H:%M:%S")  # <type 'str'>
        curr_time = "[%s %s]" % (today , now)
        #########

        if not os.path.isfile(FTP_Local_FILE):
            return

        ### 判断远端文件大小
        if self.is_same_size(FTP_Local_FILE, FTP_Remote_FILE):
            # print "### Skip the same file: %s "% FTP_Local_FILE

            abs2 = "%s Skip the same file: %s "% (curr_time, FTP_Local_FILE)
            self.WriteSeek(abs2)
            return

        buf_size = 1024
        file_handler = open(FTP_Local_FILE , 'rb')
        self.ftp.storbinary('STOR %s' % FTP_Remote_FILE , file_handler , buf_size)  # 处理上传文件

        file_handler.close()
        
        # 上传成功后，删除源文件
        os.remove(FTP_Local_FILE)
        # print "%s Upload_Complete %s ----> %s:%s" % (curr_time, FTP_Local_FILE, self.FTP_Server, FTP_Remote_FILE)        # debug info
        abs2 = "%s Upload_Complete  %s ----> %s:%s" % (curr_time, FTP_Local_FILE, self.FTP_Server, FTP_Remote_FILE)
        self.WriteSeek(abs2)


    def upload_file_tree(self, FTP_Local_DIR, FTP_Remote_DIR):
        """
        note: Upload directory function
        :param FTP_Local_DIR: local directory
        :param FTP_Remote_DIR: ftp server directory
        :return:
        """

        if not os.path.isdir(FTP_Local_DIR):            # 如果不是目录
            return
        try:                                            # 是目录执行
            self.ftp.cwd(FTP_Remote_DIR)                # FTP Server 远程目录切换
        except Exception as e:
            ### 没有解析出来
            base_dir , part_path = self.ftp.pwd() , FTP_Remote_DIR.split('/')
            for p in part_path[1:-1]:
                base_dir = base_dir + p + '/'   # 拼接子目录
                try:
                    self.ftp.cwd(base_dir)      # 切换到子目录, 不存在则异常
                except Exception as e:
                    self.ftp.mkd(base_dir)      # 不存在创建当前子目录
            ### 没有解析出来结束

        for file in os.listdir(FTP_Local_DIR):
            src = os.path.join(FTP_Local_DIR, file)         # debug info: D:\WeChatHome\Tmp\hello.txt 和 D:\WeChatHome\Tmp\help 这里有文件有目录
            if os.path.isfile(src):
                # 如果是文件，就上传
                self.upload_file(src , file)
                # print "upload file is %s" % src           # debug info: upload file is D:\WeChatHome\Tmp\hello.txt

            elif os.path.isdir(src):
                try:
                    # 如果是目录，就创建目录
                    self.ftp.mkd(file)
                except:
                    # sys.stderr.write('The dir is exists %s' % file)           # debug info: The dir is exists help
                    pass
                self.upload_file_tree(src, file)            # 递归

        self.ftp.cwd('..')

    def remote_create_dir(self, FTP_Remote_DIR):
        # type_str:
        today = datetime.date.today()
        FolderToday = today.strftime("%Y-%m-%d")  # <type 'str'>
        self.ftp.cwd(FTP_Remote_DIR)            # FTP Server 远程目录切换
        # 登录FTP后创建目录
        if FolderToday in self.ftp.nlst():
            return FolderToday
        else:
            self.ftp.mkd(FolderToday)
            return FolderToday



    def download_file(self):
        pass

    def download_file_tree(self):
        pass



if __name__ =="__main__":
    myftp = MyFTP()
    FTP_ADDR = "ftp.domain.com"
    FTP_PORT = "21"
    FTP_USER = "USER"
    FTP_PASS = "PASS"

    # The FTP server creates a directory based on the date
    today = datetime.date.today()
    today = today.strftime("%Y-%m-%d")  # <type 'str'>


    # upload directory
    FTP_LOCAL_DIRORFILE = r"/data/application/tomcat/808MediaServer/webapps/media/doc"
    FTP_REMOTE_DIRORFILE = r"/FTP_REMOTE_DIR"

    # upload file
    # FTP_LOCAL_FILE = "D:\WeChatHome\Tmp\hello.txt"
    # FTP_LOCAL_FILE = "D:\\Tools\\Navicat Premium.zip"
    # FTP_REMOTE_FILE = r"./devops/Navicat Premium.zip"

    myftp.SetFTPParams(FTP_ADDR , FTP_PORT)             # 设置FTP连接信息
    myftp.Login(FTP_USER , FTP_PASS)                    # 登录FTP

    # 登录FTP服务器后，根据日期格式创建目录
    FTP_REMOTE_DIRORFILE =  myftp.remote_create_dir(FTP_REMOTE_DIRORFILE)

    # myftp.upload_file(FTP_LOCAL_FILE, FTP_REMOTE_FILE)                        # 上传单个文件
    myftp.upload_file_tree( FTP_LOCAL_DIRORFILE, FTP_REMOTE_DIRORFILE )         # 上传整个目录

    myftp.Logout()                                      # 登出FTP
