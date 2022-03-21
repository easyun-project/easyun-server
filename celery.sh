#!/bin/bash

log='./logs/celery.log'
pid='./celery/celery.pid'

if test $1 == "start"
then
    # 启动celery守护进程
    celery multi start w1 -A run.celery --loglevel=info --logfile=$log --pidfile=$pid
elif test $1 == 'restart'
then 
    # 重启celery
    celery multi restart w1 -A run.celery --loglevel=info --logfile=$log --pidfile=$pid
elif test $1 == 'stop'
then 
    # 关闭celery
    celery multi stop w1 -A run.celery --loglevel=info --logfile=$log --pidfile=$pid
elif test $1 == 'kill'
then 
    # 杀掉celery所有进程
    ps auxww | grep 'celery' | awk '{print $2}' | xargs kill -9 
else
    echo "bad command $1 , try [start/restart/stop/kill]"
fi
 