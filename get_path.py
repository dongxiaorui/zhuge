#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#coding:utf-8
import os

def all_path(dirname):
    result = []#所有的文件
    for maindir, subdir, file_name_list in os.walk(dirname):
        #print("1:",maindir) #当前主目录
        #print("2:",subdir) #当前主目录下的所有目录
        #print("3:",file_name_list)  #当前主目录下的所有文件
        for filename in file_name_list:
            apath = os.path.join(maindir, filename)#合并成一个完整路径
            #print(apath)
            result.append(apath)
    return result

if __name__=="__main__":
    paths=all_path(r'E:\PycharmProjects\教学\zhuge\html_201903\软工17_201706014203_丁春童\unzip')
    print(paths)