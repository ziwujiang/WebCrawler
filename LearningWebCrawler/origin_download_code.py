# -*- coding: UTF8 -*-
'''
https://www.cnblogs.com/dcb3688/p/4608037.html
下载网页嵌入的flash 视频，不是容易的事。试了网上好多视频下载插件（DownLoad Helper 、 VDownLoad嗅探器、flv视频下载、ImovieBox）也么有分析出网页的链接视频。
好吧，我使用F12 调试网页工具查看网络响应，发现有type=video/mp4,然后另存为就可以了，但问题是课程有近100个，不可能一个个打开链接，
查看网页Network点击视频让其加载出type=video/mp4 类型，再另存为。这样太麻烦了。开动脑筋想用程序直接把视频下载链接分析出来，然后保存在本地。
'''
from pyquery import PyQuery as pq
import sys, os
import json
import requests
from contextlib import closing


class SaveVideo():
    LessonList = []

    def __init__(self):
        pass

    # 获取课时的列表
    def getLesson(self):
        try:
            # 该网站请求时必须带上User-Agent
            d = self.pq('http://ptr.chaoxing.com/course/2533204.html')
            DomTree = d('.p20 ul li a')
            for my_div in DomTree.items():
                URL = 'http://ptr.chaoxing.com' + my_div.attr('href')  # 课时detail URL
                l = my_div.find('.l').html()  # 课时章节NO
                r = my_div.find('.r').html()  # 课时Name
                self.LessonList.append({'url': URL, "name": l + r})
        except Exception as e:
            print(e)

        if (len(self.LessonList) > 0):
            if not os.path.exists('./Video'):
                os.makedirs('./Video')

            for lesson in self.LessonList:
                video = self.getVideo(lesson['url'])
                if video:
                    self.downloadVideo(video, lesson['name'])

            print('完成下载!!!')

    def getVideo(self, url):
        '''
        获取视频
        '''
        d = self.pq(url)
        DomTree = d("iframe")
        jsonData = DomTree.attr('data')
        video=''
        try:
            objectid = json.loads(jsonData)['objectid']  # 获取下载资源视频的对象
            downloadUrl = self.pq('http://ptr.chaoxing.com/ananas/status/' + objectid)  # 获取下载资源的URL
            video = json.loads(downloadUrl.html())['httphd']  # 在这里，我们要下载的是高清视频
        except:
            pass
        return video

    def pq(self, url, headers=None):
        '''
        将PyQuery 请求写成方法
        '''
        d = pq(url=url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'})
        return d

    def downloadVideo(self, url, file_name=''):
        '''
        下载视频
        :param url: 下载url路径
        :return: 文件
        '''
        with closing(requests.get(url, stream=True)) as response:
            chunk_size = 1024
            content_size = int(response.headers['content-length'])
            file_D='./Video/' + file_name + '.mp4'
            if(os.path.exists(file_D)  and os.path.getsize(file_D)==content_size):
                print('跳过'+file_name)
            else:
                progress = ProgressBar(file_name, total=content_size, unit="KB", chunk_size=chunk_size, run_status="正在下载",fin_status="下载完成")
                with open(file_D, "wb") as file:
                    for data in response.iter_content(chunk_size=chunk_size):
                        file.write(data)
                        progress.refresh(count=len(data))

'''
下载进度
'''
class ProgressBar(object):
    def __init__(self, title, count=0.0, run_status=None, fin_status=None, total=100.0, unit='', sep='/',
                 chunk_size=1.0):
        super(ProgressBar, self).__init__()
        self.info = "[%s] %s %.2f %s %s %.2f %s"
        self.title = title
        self.total = total
        self.count = count
        self.chunk_size = chunk_size
        self.status = run_status or ""
        self.fin_status = fin_status or " " * len(self.statue)
        self.unit = unit
        self.seq = sep

    def __get_info(self):
        # 【名称】状态 进度 单位 分割线 总数 单位
        _info = self.info % (
            self.title, self.status, self.count / self.chunk_size, self.unit, self.seq, self.total / self.chunk_size,
            self.unit)
        return _info

    def refresh(self, count=1, status=None):
        self.count += count
        # if status is not None:
        self.status = status or self.status
        end_str = "\r"
        if self.count >= self.total:
            end_str = '\n'
            self.status = status or self.fin_status
        print(self.__get_info(), end=end_str)


if __name__ == '__main__':
    C = SaveVideo()
    C.getLesson()
    sys.exit()