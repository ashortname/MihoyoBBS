# MihoyoBBS
Mihoyo BBS, HonkaiImpact , Reptile program

米哈游的bbs论坛的爬虫程序。

# 调用方法
##  1.手动输入链接
  ### topicDetailParser(url, parseCtl, isGood=False, isHot=False)
	
  * url(string)   : 主页面地址
  
  * parseCtl(int) : 爬取次数，默认为 10
  
  * isGood(bool)  : 按照“精华”排序，默认为 False
  
  * isHot(bool)   : 按照“热门”排序，默认为 False
  
  * 当 isGood = isHot = False 时，默认按照“最新”排序
  
  
##  2.通过分类爬取
   ###  depParse(getType, parseCtl = 10, isGood = False, isHot = False, sort = 'create', GFNType = 1)
    
  * getType(tiltleType) : 自定义在 MihoyoBBs 的 “titleType” 中
   
  * parseCtl(int) : 爬取次数，默认为 10
   
  * isGood(bool)  : 按照“精华”排序，默认为 False

  * isHot(bool)   : 按照“热门”排序，默认为 False
  
  * sort(string)  : 用于“问答”爬取， 默认为 “create”
  
  * GFNType(int)  : 官方的新闻类型，包括“2 - 活动”，“1 - 公告”，“3 - 资讯”，默认为 1
  
  * depParse的调用顺序：
      
      depPase -> depJsonParser -> searchArticles -> getContent -> print_page -> downloadImgs 
      

## 详细使用可以参照test.py 并且代码注释很详细
