import os
import socket
from configparser import ConfigParser
from urllib.parse import quote

from bs4 import BeautifulSoup
import urllib
import urllib.request
import sys
import io
import time

import spider_paper

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')

page_num=15
#index_url='http://search.cnki.com.cn/Search.aspx?q=%E6%A0%91&rank=relevant&cluster=Type&val=D049&p='  #+str(page_num)


def get_paper_url(page_url):
    html = urllib.request.urlopen(page_url).read()
    soup = BeautifulSoup(html,'html.parser')
    #print(soup.find_all('div', class_='wz_content',a))
    #pp=soup.findAll('a',attrs={'href':re.compile('^http'),'id':'link1'})
    f = open('data-detail.txt','a+', encoding='utf-8')
    all = soup.find_all('div', class_='wz_content')
    for string in all:
        item = string.find('a', target='_blank')#文章标题与链接
        href = item.get('href')# 获取文章url
        title = item.get_text() # 获取文章标题
        year_count = string.find('span', class_='year-count')#获取文章出处与引用次数
        #year_count = year_count.get_text()
        publish = ''
        reference = ''
        for item in year_count:
            item = item.string
            item = item.replace('\n','')
            item = item.replace('\r', '')
            if '被引次数' in item:
                reference = item# 获取被引次数
            elif '年' in item: # 获取文章出处
                publish = item
            print(publish)
            print(reference)
        #print(year_count)
        f.write(href + '\t' + title + '\t' + publish + '\t' + reference +'\n')
    f.close()

if __name__ == '__main__':
    start = time.clock()
    cf = ConfigParser()
    cf.read("Config.conf", encoding='utf-8')
    keyword = cf.get('base', 'keyword')# 关键词
    maxpage = cf.getint('base', 'max_page')# 最大页码
    current_page = cf.getint('base', 'currentpage')  # 读取currentPage
    if os.path.exists('data-detail.txt') and current_page == 0:
        print('存在输出文件，删除该文件')
        os.remove('data-detail.txt')

    index_url='http://search.cnki.com.cn/Search.aspx?q='+quote(keyword)+'&rank=&cluster=&val=&p='#quote方法把汉字转换为encodeuri?
    print(index_url)
    for i in range(current_page, maxpage):
        page_num=15
        page_str_num=i*page_num
        page_url=index_url+str(page_str_num)
        #get_page_url(i)
        print(page_url)
        attempts = 0
        success = False
        while attempts < 10 and not success:
            try:
                get_paper_url(page_url)
                socket.setdefaulttimeout(10)  # 设置10秒后连接超时
                success = True
            except:
                attempts += 1
                print("第"+str(attempts)+"次重试！！")
                if attempts == 10:
                    break
        cf.set('base', 'currentpage', str(i))
        cf.write(open("Config.conf", "w", encoding='utf-8'))
    spider_paper.spider_paper()# spider_paper补全文章信息
    end = time.clock()
    print ('Running time: %s Seconds'%(end-start))
