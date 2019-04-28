#! /bin/bash/python3
# -*- coding: utf-8 -*-
import datetime
from MihoyoBBS import MihoyoBBs

"""
##  程序入口
"""
if __name__ == '__main__':
    try:
        ## 本地存储路径
        localRootPath = "D:\\Program\\Python\\Temp"
        ## 控制爬取次数
        parseControl = 10
        ## 爬取起点
        mainUrl1 = "https://bbs.mihoyo.com/bh3/topicDetail/65"
        '''
        一切的开始
        '''
        mainUrl = "https://bbs.mihoyo.com/bh3"
        ##########################
        ##  开始爬取
        ##########################
        ## 开始时间
        startTime = datetime.datetime.now()
        print("------ 开始爬取：{0} ------".format(startTime.strftime("%Y-%m-%d %H:%M:%S")))
        ## Parser(mainUrl)
        '''
        ## 下面是调用自定义类实现的
        '''
        Mihoyo = MihoyoBBs(localRootPath)
        #Mihoyo.depParse("官方", parseCtl=5, GFNType=3)
        Mihoyo.topicDetailParser(mainUrl1, 2)
        endTime = datetime.datetime.now()
        print("------ 本次爬取结束：{0} ------".format(endTime.strftime("%Y-%m-%d %H:%M:%S")))
        print("================================\n\t总计花费时间：{0} 秒。\n================================\n".format((endTime - startTime).seconds))
    except Exception as aa:
        print("main:{0}".format(aa))