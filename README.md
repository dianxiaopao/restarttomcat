# restarttomcat
an python shell to  restart tomcat
自动重启tomcat脚本

亦可以通过部署 成为开机启动脚本
#主要修改以下两个文件的环境变量，缺一不可：

##一： /rc.local文件
###vim /etc/rc.d/rc.local
#####/etc/rc.d/rc.local和/etc/rc.local其实是一个文件，软链接
####文件头部 原来是 #!/bin/bash 
####修改为 #!/bin/bash -x  可以记录所有日志
##加入命令 以下两条命令



###1.
######export PATH=/usr/local/java/jdk1.8.0_73/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/usr/local/mysql/bin:/root/bin
######注意：环境变量可以使用 echo $PATH 查看
######手动的设置环境变量，因为系统开机过程中 环境变量无法读取
###2.
######/usr/bin/python /usr/local/src/startserver.py

######此时 确保 /etc/rc.d/rc.local是可执行文件
######如果不是 赋予x权限
######chmod +x /etc/rc.d/rc.local
######二：/etc/bashrc
######加入如下命令

######export PATH=/usr/local/java/jdk1.8.0_73/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/usr/local/mysql/bin:/root/bin



######以上两条缺一不可
