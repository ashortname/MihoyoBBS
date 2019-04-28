#! /bin/bash/python3
# -*- coding: utf-8 -*-
import requests
import json
from bs4 import BeautifulSoup

# 崩坏3 mihoyo 官方论坛 : https://bbs.mihoyo.com/bh3/
# 可用于提取相关话题
# 2019.04.28

"""
##  article页面模型
"""
class _OnePage:
    def __init__(self, url):
        self.url = url
        self.title = ""
        self.list_ImgUrls = []
        self.text = ""
        self.list_replies = []

"""
##  工具类封装
"""
class MihoyoBBs:

    """
    ## 构造函数
    """
    def __init__(self, localPath):
        self.__parseControl = 10    ## 默认只获取 10 页
        self.__localRootPath = localPath    ## 根目录
        self.ParseCount = 0
        self.currentType = "Topic"
        self.PageSize = 10
        #   方便的字典，包含每种类型的基础链接
        self.__titleType = {
            "首页": ["", "https://api-static.mihoyo.com/api/community/forum/home/mobileHomeInfo?gids=1&page={0}&num={1}", "hots"],
            "甲板": ["1", "https://api-community.mihoyo.com/community/forum/home/forumPostList?gids=1&forum_id=1&is_good={0}&is_hot={1}&sort={2}&last_id={3}&page_size={4}", "list"],
            "攻略": ["14", ""],
            "官方": ["6", "https://api-community.mihoyo.com/community/forum/home/news?gids=1&last_id={0}&type={1}&page_size={2}", "list"],
            "图片": ["4", ""],
            "问答": ["21", ""],
            "反馈": ["5", ""]
        }

    """
    ## 构造http头
    """
    def __buildHeader(self, referer):
        return {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': referer,
            'Origin': 'https://bbs.mihoyo.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
        }

    """
    ##  拼接绝对路径
    """
    def __getCompleteUrl(self, url, ContainsAll = True, ArticleId = 0):
        if ContainsAll is True:
            return str.format("https://bbs.mihoyo.com/{0}", url)
        else:
            return str.format("https://bbs.mihoyo.com/bh3/article/{0}", ArticleId)

    """
    ##  构造”加载更多“请求链接
    """
    def __loadMoreUrl(self, getType, **dicArgs):
        try:
            if getType == "首页":
                return self.__titleType[getType][1].format(dicArgs['page'], dicArgs['num'])
            if getType == "甲板":
                return self.__titleType[getType][1].format(
                    dicArgs['is_good'], dicArgs['is_hot'], dicArgs['sort'], dicArgs['last_id'], dicArgs['pagesize'])
            if getType == "官方":
                return self.__titleType[getType][1].format(dicArgs['last_id'], dicArgs['type'], dicArgs['pagesize'])
        except Exception as exception:
            print("An error occurred at function [loadMoreUrl]: {0} \n\tat args {1}".format(exception, dicArgs))

    """
    ##  构造请求地址
    ##  主题的主页面
    """
    def __buildReqUrl(self, typeValue):
        return "https://bbs.mihoyo.com/bh3/{0}".format(typeValue)

    """
    ##  指定类的序列化，转为json数据
    """
    def __dictPage(self, std):
        return {
            'url': std.url,
            'title': std.title,
            'text': std.text,
            'images': std.list_ImgUrls,
            'replies': std.list_replies
        }

    """
    ##  提取具体话题页内容
    """
    def __getContent(self, pageObj):
        try:
            with requests.get(url=pageObj.url, headers=self.__buildHeader(pageObj.url), timeout=5) as responseContent:
                responseContent.encoding = "utf8"
                bs_obj = BeautifulSoup(responseContent.text, 'html.parser')
                pageObj.title = bs_obj.find('h1', {'class': 'mhy-article-page__title'}).get_text()
                ## 页面的内容可能不在 class 为 “mhy-img-text-article__content ql-editor”里
                ## 所以要进行判断
                _Text = bs_obj.find('div', {'class': 'mhy-img-text-article__content ql-editor'})
                _Text2 = bs_obj.find('p', {'class': 'mhy-img-article__describe'})
                if _Text is not None:
                    pageObj.text = _Text.get_text()
                elif _Text2 is not None:
                    '''这是另一种情况'''
                    pageObj.text = _Text2.get_text()
                else:
                    pageObj.text = ""
                ## 获取图片链接
                '''preview'''
                imgUrls = bs_obj.find_all('img', {'preview': 'imgPreview'})
                for _link in imgUrls:
                    ## 这里的图片路径就是绝对路径
                    pageObj.list_ImgUrls.append(_link.get('large'))
                ## 获取评论
                '''不能获取楼中楼的内容，待改进...'''
                replies = bs_obj.find_all('div', {'class': 'reply-card__content'})
                for _reply in replies:
                    if _reply is not None:
                        contentText = _reply.get_text()
                        if contentText is not '':
                            pageObj.list_replies.append(contentText)
                ## 结束一次爬取，打印结果并保存
                self.__print_page(pageObj)
                ## 添加进表内
                '''作为扩展吧，或者是记录'''
                ## all_ArticlePages.append(pageObj.url)
        except Exception as exception:
            print("An error occurred at function [getContent]: {0} at url \'{1}\'".format(exception, pageObj.title))

    """
    ##  打印页面内容并保存结果
    """
    def __print_page(self, pageObj):
        import os
        import re
        try:
            ## 创建文件夹
            path = str.format("{0}\\{1}\\{2}", self.__localRootPath, self.currentType,
                              re.sub(r'[\\:/<>?|\"*]*', '', pageObj.title.strip()))
            if not os.path.exists(path):
                os.makedirs(path)
            ## 下载图片
            self.__downloadImgs(pageObj, path)
            with open(str.format("{0}\\PageInfo.json", path), 'w+', encoding='utf-8') as file:
                ## 以json文件的格式存储信息
                ## “ensure_ascii = False” 防止中文乱码或报错
                json.dump(pageObj, file, default=self.__dictPage, ensure_ascii=False)
                ###################################
                ##  下面输出的是控制台提示信息
                ###################################
                print("\n================>>>>>>>>>")
                print("Title: {0}\nUrl: {1}\nContentText: {2}\n".format(
                    pageObj.title, pageObj.url, pageObj.text))

                print("ImgUrls:")
                for url in pageObj.list_ImgUrls:
                    print(">>> {0}".format(url))

                print("Replies:")
                for reply in pageObj.list_replies:
                    print("--- {0}".format(reply))
        except Exception as exception:
            print("An error occurred at function [print_page]: {0} at url : \'{1}\'".format(exception, pageObj.url))

    """
    ##  下载图片
    """
    def __downloadImgs(self, pageObj, path):
        try:
            ## 主要还是为了图片命名
            count = 1
            for url in pageObj.list_ImgUrls:
                ## 获取图片
                with requests.get(url=url, headers=self.__buildHeader(pageObj.url), timeout=5) as img:
                    ## 保存到本地
                    ## 获取扩展名
                    temp = url.split(',')
                    extension = temp[len(temp) - 1]
                    with open(str.format("{0}\\{1}.{2}", path, count, extension), 'wb+') as file:
                        file.write(img.content)
                    ## 计数器加
                    count += 1
        except Exception as exception:
            print("An error occurred at function [downloadImgs]: {0} at url : \'{1}\'".format(exception, pageObj.url))

    """
    ##  装填页面并爬取
    ##  进行内容页爬取的函数
    """
    def __searchArticles(self, linkList):
        try:
            for _link in linkList:
                ##  控制
                if self.ParseCount is self.__parseControl:
                    return  -1
                ##  爬取
                pageTemp = _OnePage(self.__getCompleteUrl("", False, _link['post_id']))
                self.__getContent(pageTemp)
                ##  计数器
                self.ParseCount += 1
            return 0
        except Exception as exception:
            print("An error occurred at function [searchArticles]: {0} \nat list : \'{1}\'".format(exception, linkList))

    """
    ##  解析网页，提取话题链接
    ##  只针对话题页
    """
    def topicDetailParser(self, url, parseCtl, isGood=False, isHot=False):
        try:
            if 'topicDetail' not in url:
                print("Unsupport url for this function...")
                return
            ##  设置爬取次数
            self.__parseControl = parseCtl
            ##  计数归零
            self.ParseCount = 0
            with requests.get(url=url, headers=self.__buildHeader(url), timeout=5) as responseContent:
                responseContent.encoding = "utf8"
                bs_obj = BeautifulSoup(responseContent.text, 'html.parser')
                all_card_links = bs_obj.find_all('a', {'class': 'mhy-article-card__link', 'target': '_blank'})
                ##  调用装填页面并爬取
                for _link in all_card_links:
                    ## 控制爬取次数
                    if self.ParseCount is self.__parseControl:
                        break
                    ## 每张主页的链接
                    pageTemp = _OnePage(self.__getCompleteUrl(_link.get('href')))
                    ## 提取主页里的内容
                    self.__getContent(pageTemp)
                    ## 计数器加1
                    self.ParseCount += 1
            ##  加载更多
            if self.ParseCount is not self.__parseControl:
                last_id = all_card_links[len(all_card_links) - 1].get('href').split('/')[3]
                tmp = url.split('/')
                topicId = tmp[len(tmp) - 1]
                while True:
                    moreUrl = "https://api-community.mihoyo.com/community/forum/topic/topicPostList?" \
                              "gids=1&topic_id={0}&page_size={1}&last_id={2}&is_good={3}&is_hot={4}".format(
                        topicId, self.PageSize, last_id, isGood, isHot
                    )
                    if self.__depJsonParser('甲板', moreUrl, url, 0, last_id) is -1:
                        return
        except Exception as exception:
            print("An error occurred at function [topicDetailParser]: {0} \nat url : \'{1}\'".format(exception, url))

    """
    ##  更深度的爬取
    ##  基于js链接
    """
    def depParse(self, getType, parseCtl = 10, isGood = False, isHot = False, sort = 'create', GFNType = 1):
        try:
            ##  设置爬取次数
            self.__parseControl = parseCtl
            ##  计数归零
            self.ParseCount = 0
            ##  判断类型
            self.currentType = getType
            if getType not in self.__titleType.keys():
                print("Unsupported type...\n")
                return
            ##  构造referer时用到
            requestUrl = self.__buildReqUrl(self.__titleType[getType][0])
            if getType == "首页":
                Page = 0
                while True:
                    moreUrl = self.__loadMoreUrl(getType, page=Page, num=self.PageSize)
                    if self.__depJsonParser(getType, moreUrl, requestUrl, Page, "") is -1:
                        return
            if getType == "甲板":
                last_id = ""
                while True:
                    moreUrl = self.__loadMoreUrl(getType, is_good=isGood, is_hot=isHot, sort=sort, last_id=last_id, pagesize=self.PageSize)
                    if self.__depJsonParser(getType, moreUrl, requestUrl, 0, last_id) is -1:
                        return
            if getType == "官方":
                last_id = ""
                while True:
                    moreUrl = self.__loadMoreUrl(getType, last_id=last_id, type=GFNType, pagesize=self.PageSize)
                    if self.__depJsonParser(getType, moreUrl, requestUrl, 0, last_id) is -1:
                        return
        except Exception as exception:
            print("An error occurred at function [depParse]: {0} \nat type : \'{1}\'".format(exception, getType))

    """
    ##  进行json数据获取
    """
    def __depJsonParser(self, getType, moreUrl, requestUrl, Page, last_id):
        try:
            ##  提取
            with requests.get(moreUrl, headers=self.__buildHeader(requestUrl), timeout=5) as responseContent:
                responseContent.encoding = "utf8"
                resultJson = responseContent.json()
                ##  如果获取成功
                if resultJson['retcode'] is 0:
                    users = resultJson['data'][self.__titleType[getType][2]]
                    if getType == "首页":
                        ##  下一页
                        Page += 1
                    else:
                        last_id = users[len(users) - 1]['post_id']
                    ##  控制次数
                    if self.__searchArticles(users) is -1:
                        return -1
                    return 0
                else:
                    return -1
        except Exception as exception:
            print("An error occurred at function [depJsonParser]: {0} \nat type : \'{1}\'".format(exception, getType))