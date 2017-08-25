#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
@author:zhangbin 
@Create date:  2017-6-29 15:47:05 
@description 自动重启 misrobot-service  misrobot-web  platform   需在serverpath中配置tomcat和platform的路径。
@version:1.0
'''

import subprocess
import re
import xml.dom.minidom
import ConfigParser
import os
import sys
import logging
from os import path
reload(sys)
sys.setdefaultencoding('utf8')

'''
    日志模块
'''
def setLog():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Log等级总开关

    # 第二步，创建一个handler，用于写入日志文件
    logfile = os.path.join(path.dirname(__file__), 'logger.txt')
    fh = logging.FileHandler(logfile, mode='w')
    fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关

    # 第三步，再创建一个handler，用于输出到控制台
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)  # 输出到console的log等级的开关

    # 第四步，定义handler的输出格式
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # 第五步，将logger添加到handler里面
    logger.addHandler(fh)
    logger.addHandler(ch)
'''
    读取 配置文件，获取相关路径
'''
def getConfig():
    cp = ConfigParser.SafeConfigParser()
    d = path.dirname(__file__)  # 返回当前文件所在的目录
    confpath = os.path.join(d, 'serverpath.conf')
    cp.read(confpath)
    global tomcatservicepath
    tomcatservicepath = cp.get('path', 'tomcat-service')
    global tomcatwebpath
    tomcatwebpath = cp.get('path', 'tomcat-web')
    global platformpath
    platformpath = cp.get('path', 'platform')


'''
读取platform 配置文件，获取 端口
'''


def getPlatformPort(configpath):
    with open(configpath) as config:
        txt = config.read()
        # logging.debug(txt)
        regroup = re.search(r'.*httpserverport.*=(.*\w*)', txt)
        if regroup is not None:
            logging.debug(u'platform端口为:' + regroup.group(1))
            return regroup.group(1).strip()
        else:
            return -1


'''
打开文档读取tomcat 配置文件 server.xml文件
'''


def getTomcatPort(xmlpath):
    try:
        # 打开xml文档
        dom = xml.dom.minidom.parse(xmlpath)
        # 得到文档元素对象
        root = dom.documentElement
        itemlist = root.getElementsByTagName('Connector')
        item = itemlist[0]
        port = item.getAttribute("port")
        logging.debug(xmlpath + u'端口为:' + port)
        return port
    except:
        logging.debug(u'获取' + xmlpath + '端口失败')
        return -1


'''
启动tomcat
'''


def startTomcatServer(path):
    # 查询端口
    xmlpath = os.path.join(path, 'conf', 'server.xml')
    port = getTomcatPort(xmlpath)
    if (port == -1):
        logging.debug(path + u'的端口读取失败')
        return
    # 查询端口进程
    # grep -w 精确匹配
    str = "ss -tnlp | grep -w :::" + port
    #或者直接获取 pid   ss -tnlp |grep 18086 | awk '{print $6}'|awk -F  ',' '{print $2}'| awk -F '=' '{print $2}'
    #直接返回 pid数值 如242
    res = subprocess.Popen(str, stdout=subprocess.PIPE, shell=True)
    tomcats = res.stdout.readlines()
    if (len(tomcats) == 0):
        # 未找到进程，不执行
        logging.debug(path + u'的端口' + port + '未启动，不杀进程')
    else:
        pid = re.search(r'.*pid=(\w*)', tomcats[0]).group(1)
        # 杀掉进程
        cmdstr = 'kill -9 ' + pid
        subprocess.Popen(cmdstr, stdout=subprocess.PIPE, shell=True)
    # 启动进程
    binpath = os.path.join(path, 'bin', 'startup.sh')
    subprocess.check_call(binpath, shell=True)


'''
启动 platform
'''


def startPlatformServer(path):
    # 查询端口
    xmlpath = os.path.join(path, 'config')
    port = getPlatformPort(xmlpath)
    if (port == -1):
        logging.debug(path + u'的端口读取失败')
        return
        # grep -w 精确匹配
    str = "ss -tnlp | grep -w :::" + port
    logging.debug(str)
    res = subprocess.Popen(str, stdout=subprocess.PIPE, shell=True)
    stdline = res.stdout.readlines()
    if (len(stdline) == 0):
        # 未找到进程，不执行
        logging.debug (path + u'的端口' + port + '未启动，不杀进程')
    else:
        regroup = re.search(r'.*pid=(\w*)', stdline[0])
        if regroup is not None:
            pid = regroup.group(1)
        else:
            pid = -1
        # 杀掉进程
        cmdstr = 'kill -9 ' + pid
        subprocess.Popen(cmdstr, shell=True)
    # 启动进程
    binpath = os.path.join(path, 'start_server.sh')
    logging.debug('tomcat path= ' + binpath)
    subprocess.check_call(binpath, shell=True, env=os.environ)


if __name__ == "__main__":
    setLog()
    logging.debug(u'开始执行....')
    getConfig()
    # 重启tomcat-service
    if tomcatservicepath is not None:
        logging.debug(u'重启tomcat-service 中...')
        startTomcatServer(tomcatservicepath)
    # 重启tomcat-web
    if tomcatwebpath is not None:
        logging.debug(u'重启tomcat-tomcat-web 中...')
        startTomcatServer(tomcatwebpath)
    # 重启platform
    if platformpath is not None:
        logging.debug(u'重启platform 中....')
        startPlatformServer(platformpath)
    logging.debug(u'重启完成')
