#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#coding:utf-8
import poplib
import email
import datetime
import time
import os
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
import pymysql
import unzip
import get_path
from bs4 import BeautifulSoup
import read_file

#数据库连接字符串
conn = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        db='zhuge_db',
        port=3306,
        charset='utf8'
    )
#日志的路径
path_log="log.txt"
f_log= open (path_log,'a')

# 输入邮件地址, 口令和POP3服务器地址:
email = ''
password = ''
pop3_server = ''


def decode_str(s):  # 字符编码转换
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value

def get_email_headers(msg):
    headers = {}
    for header in ['From', 'To', 'Cc', 'Subject', 'Date']:
        value = msg.get(header, '')
        if value:
            if header == 'Date':
                headers['Date'] = value
            if header == 'Subject':
                subject = decode_str(value)
                headers['Subject'] = subject
            if header == 'From':
                hdr, addr = parseaddr(value)
                #name = decode_str(hdr)
                #from_addr = u'%s <%s>' % (name, addr)
                #headers['From'] = from_addr
                headers['From'] = addr
            if header == 'To':
                all_cc = value.split(',')
                to = []
                for x in all_cc:
                    hdr, addr = parseaddr(x)
                    name = decode_str(hdr)
                    #to_addr = u'%s <%s>' % (name, addr)
                    to_addr = addr
                    to.append(to_addr)
                headers['To'] = ','.join(to)
            if header == 'Cc':
                all_cc = value.split(',')
                cc = []
                for x in all_cc:
                    hdr, addr = parseaddr(x)
                    name = decode_str(hdr)
                    cc_addr = u'%s <%s>' % (name, addr)
                    cc.append(to_addr)
                headers['Cc'] = ','.join(cc)
            #if header == 'Body':
            #    headers['Body'] = decode_str(value)
    return headers

def get_email_content(message, savepath):
    attachments = []
    time_flag=time.strftime("%Y%m%d%H%M%S", time.localtime())+"_"
    for part in message.walk():
        filename = part.get_filename()
        if filename:
            filename = decode_str(filename)
            data = part.get_payload(decode=True)
            abs_filename = os.path.join(savepath, time_flag+filename)
            attach = open(abs_filename, 'wb')
            attachments.append(filename)
            attach.write(data)
            attach.close()
    return attachments

def who(strs,users):
    result=[]
    for str in strs:
        for user in users:
            if user[0] in str:
                result.append(user[0]+'_'+user[1]+'_'+user[2])
            elif user[1] in str:
                result.append(user[0]+'_'+user[1]+'_'+user[2])
    return result


#读取数据表
cursor = conn.cursor() #数据库游标
cursor.execute('select `name`,`number`,`class` from `users`')
users = cursor.fetchall()

# 连接到POP3服务器,有些邮箱服务器需要ssl加密，对于不需要加密的服务器可以使用poplib.POP3()
server = poplib.POP3_SSL(pop3_server)
server.set_debuglevel(1)
# 打印POP3服务器的欢迎文字:
print(server.getwelcome().decode('utf-8'))
# 身份认证:
server.user(email)
server.pass_(password)
# 返回邮件数量和占用空间:
print('Messages: %s. Size: %s' % server.stat())
# list()返回所有邮件的编号:
resp, mails, octets = server.list()
# 可以查看返回的列表类似[b'1 82923', b'2 2184', ...]
print(mails)
index = len(mails)
print('共收到邮件',index,'封',file=f_log)
for i in range(1,index+1):
    # 倒序遍历邮件
    resp, lines, octets = server.retr(i)
    # lines存储了邮件的原始文本的每一行,
    # 邮件的原始文本:
    msg_content = b'\r\n'.join(lines).decode('utf-8')
    # 解析邮件:
    msg = Parser().parsestr(msg_content)
    # 获取邮件时间
    #date1 = time.strptime(msg.get("Date")[0:24], '%a, %d %b %Y %H:%M:%S')  # 格式化收件时间
    #date2 = time.strftime("%Y%m%d", date1)  # 邮件时间格式转换
    #if (date2 < '20190306') | (date2 > '20190314'):
    #    continue
    # 获取邮件详细内容
    headers = get_email_headers(msg)
    # 根据学生姓名计算保存文件夹
    students=who({headers['Subject']}, users)  # ,headers['Body']
    for student in students:
        user_name,user_number,user_class=student.split('_')
        path_file=user_class+'_'+user_number+"_"+user_name
        # 遍历下载下来的文件，如果有zip或rar格式，则解压到该目录下的unzip文件夹内
        path_download='E:\\PycharmProjects\\教学\\zhuge\\html_201903\\'+path_file
        print(path_download)
        if os.path.exists(path_download)==False:
            os.mkdir(path_download)
        attachments = get_email_content(msg, path_download)
        # 输出信息
        print(path_file,file=f_log)
        print('subject:', headers['Subject'],file=f_log)
        print('from:', headers['From'],file=f_log)
        #print('to:', headers['To'],file=f_log)
        if 'cc' in headers:
            print('cc:', headers['Cc'],file=f_log)
        print('date:', headers['Date'],file=f_log)
        #print('body:', headers['Body'],file=f_log)
        print('attachments: ', attachments,file=f_log)
        #print('++++++++++++++++++++++++++++',file=f_log)
        # 遍历下载下来的文件
        #print('Download:',path_download,file=f_log)
        list_download = os.listdir(path_download)
        for i in range(0,len(list_download)):
            print('Include:',list_download[i],file=f_log)
            path_tmp = os.path.join(path_download,list_download[i])
            extension=os.path.splitext(path_tmp)[1]
            if extension.lower()=='.zip':
                unzip.unzip_file(path_tmp,path_download+'\\unzip\\')
                print('unzip:'+path_tmp)
            elif extension.lower() == '.rar':
                unzip.unrar_file(path_tmp, path_download + '\\unzip\\')
                print('unrar:', path_tmp)
            else:
                print('not find .zip or .rar')
        #遍历目录
        path_real=path_download
        #if os.path.exists(path_download+'\\unzip'):
        #    path_real = path_download+'\\unzip'
        #files=get_path.all_path(path_real)
        files=get_path.all_path(path_real)
        tags = []
        file_number=0
        for file in files:
            #print(file,file=f_log)
            extension = os.path.splitext(file)[1]
            if extension.lower()=='.html' or extension.lower()=='.txt':
                file_number+=1
                print(file,file=f_log)
                print('后缀:', extension)
                html=read_file.read(file)
                #print(html)
                soup = BeautifulSoup(html, 'html.parser')
                if soup.html:
                    childs=soup.html.descendants
                elif soup.body:
                    childs=soup.body.descendants
                else:
                    childs=[]
                for child in childs:
                    if child.name not in tags:
                        tags.append(child.name)
        print(tags,file=f_log)
        print('html tags number：',len(tags),file=f_log)
        if file_number>1:
            print('[备注]：存在多个文件！',file=f_log)
        print('-----------------------------',file=f_log)
        cursor.execute('update `users` set `email`="'+headers['From']+'",`html`='+str(len(tags))+' where `number`="'+user_number+'";')
        conn.commit()
        #f_list = get_att(msg)  # 获取附件
        # print_info(msg)
server.quit()