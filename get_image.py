# https://www.umei.cc/

import os,re
import requests
import time,random
from bs4 import BeautifulSoup
class Spider:
    def __init__(self, headers):
        self.headers = headers

    def pause(self):
        '''
        TODO: 用于模拟人工操作，添加时间间隔，避免给网站造成压力
              随机暂停1-3s
        '''
        # pass
        time.sleep(random.randint(1,3))

    def requestsImage(self, url=""):
        '''
        TODO: 请求图片数据,返回二进制数据
        '''
        self.pause()
        try:
            response = requests.get(url=url, headers=self.headers)
            response = response.content
        except Exception as e:
            print("图片请求发生错误，错误代码为:",e)
            response = None
        return response
        
        
    def requestsHtml(self, url=""):
        '''
        TODO: 请求网页
        '''
        self.pause()
        try:
            response = requests.get(url=url, headers=self.headers)
            response.encoding='utf-8'
            print("response.status_code:",response.status_code)
            response = response.text
            
        except Exception as e:
            print("网页请求发生错误，错误代码为:",e)
            response = None
        # print(response.text)
        return response

    def parserUrl(self, html):
        '''
        TODO: 用于解析获取图片的URL，由于部分源码中不包含alt内容，故采用bs4解析
        '''
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        for div in soup.find_all('div', class_='big-pic'):
            img_tag = div.find('img')
            alt = img_tag.get('alt') if img_tag else ''
            src = img_tag['src'] if img_tag else ''
            results.append((alt, src))

        print("BeautifulSoup->results:",results)
        return results

    
    def parserHtml(self, pattern, html):
        '''
        TODO: 解析网页，根据正则获得相应的链接，返回items，为列表数据
        '''
        pattern = re.compile(pattern)
        items = re.findall(pattern, html)
        # print(items)
        return items
    
    def parserEachTypeFinalNum(self, html,pattern):
        '''
        TODO: 用于解析网页，获得单一套图总页数
        '''
        finalNumber = re.findall(pattern,html)
        print("finalNumber:",finalNumber)
        if not finalNumber: #若列表为空
            number = 1
        else:
            number = finalNumber[0]
        return number

    def saveImage(self, content,imgpath,imgname):
        '''
        TODO: 用于保存图片
        '''
        try:
            with open(imgpath+imgname,'wb')as fw:
                fw.write(content)
        except:
            print("文件写入失败！")
            pass

    def createDir(self,path):
        if not os.path.exists(path):
            print('当前 "{}" 文件夹不存在，即将创建文件夹...'.format(path))
            try:
                os.mkdir(path)
                print("文件夹创建成功！")
            except Exception as e:
                print("文件夹创建失败，错误原因为:",e)
                pass
        else:
            pass

if __name__ == "__main__":
    url="https://www.umei.cc/meinvtupian/"
    headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        "Referer": "https://www.umei.cc/meinvtupian/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    }
    spider = Spider(headers)
    html1 = spider.requestsHtml(url) 
    pattern = '<span><b>&nbsp;</b><h2><a href="/meinvtupian/(.*?)">(.*?)</a></h2></span>'
    type_items = spider.parserHtml(pattern, html1) # 获得对应的9个类型
    all_starttime = time.time()
    for item in type_items: # 根据获取到的每个类型url，分别请求网页，
        each_type_starttime = time.time()
        each_type_url = url+item[0]
        print("each_type_url:",each_type_url) # each_type_url: https://www.umei.cc/meinvtupian/xingganmeinv/
        kind_name = item[1]
        print(kind_name) 
        spider.createDir(kind_name)

        # 获得当前type的总页数 
        html2 = spider.requestsHtml(each_type_url)
        # print("html2:",html2)   #<a href="/meinvtupian/siwameinv/index_45.htm">尾页</a></div>
        pattern_each_type_num = '<a href="/meinvtupian/.*?/index_(\d+).htm">尾页</a></div>'
        finalNum = spider.parserEachTypeFinalNum(html2,pattern_each_type_num)

        pattern_each_type_url = '<div class="title"><span><a href="/meinvtupian/(.*?)">(.*?)</a></span></div>'
        for i in range(1,int(finalNum)+1):
            # if i == 2: # 若正常爬取内容时，可将这三行注释掉
            #     print("套图内容测试，即将跳至下一类型！")
            #     break
            if i == 1:
                kind_items = spider.parserHtml(pattern_each_type_url, html2)
            else:
                kind_url = each_type_url+"index_{}.htm".format(i)  # 获得每页的单一套图地址
                # 根据类型套图的地址请求，获得单一套图的地址
                html3 = spider.requestsHtml(kind_url)
                kind_items = spider.parserHtml(pattern_each_type_url, html3)
                if not kind_items:
                        continue
            

            # for kitem in kind_items[:2]:  # 这行用于测试使用，仅获取两组图片内容，正常爬取时可用下面的代码
            for kitem in kind_items: 
                kname = kitem[1]
                kurl = "https://www.umei.cc/meinvtupian/"+kitem[0] # 先请求第一页，然后获取总页数
                print("kurl:",kurl)
                html4 = spider.requestsHtml(kurl)
                pattern_each_kind_num = '<a href="/meinvtupian/.*?/\d+_(\d+).htm">尾页</a>'
                each_final_num = spider.parserEachTypeFinalNum(html4,pattern_each_kind_num)
                print("each_final_num:",each_final_num)

                # 构建新的url
                for k in range(1, int(each_final_num)+1):
                    # if k == 2:  # 和上面一样，用于测试
                    #     print("测试！即将跳至下一组...")
                    #     break
                    if k == 1:
                        img_url = "https://www.umei.cc/meinvtupian/"+kitem[0] # 先请求第一页
                    else:
                        img_url = "https://www.umei.cc/meinvtupian/"+kitem[0].split('.')[0]+'_{}.htm'.format(k)
                    print("img_url:",img_url)
                    # 获取图片url
                    # pattern_img = '<div class="big-pic"><a href="/meinvtupian/.*?.htm"><img alt="(.*?)" src="(.*?)"/></a></div>'
                    pattern_img = 'div class="big-pic">.*?\s+src="([^"]*)"'
                    html5 = spider.requestsHtml(img_url)
                    if not html5:
                        continue
                    # real_img_url = spider.parserHtml(pattern_img, html5)
                    real_img_url = spider.parserUrl(html5)
                    print("real_img_url:",real_img_url)
                    for img in real_img_url:
                        if not img[0]:
                            imgPathName=""
                        else:
                            imgPathName = img[0]
                        imgName = img[1].split('/')[-1]
                        imgUrl = img[1]
                        content = spider.requestsImage(imgUrl)
                        if not content:
                            continue
                        # print('-----> {}/{}/'.format(kind_name,imgPathName))
                        imgPath = '{}/{}/'.format(kind_name,imgPathName)
                        spider.createDir(imgPath)
                        spider.saveImage(content,imgPath,imgName)
                    print("已获取{}/{}张图片".format(k,each_final_num))
        print("爬取一组图片共耗时:{:.2f}min".format((time.time()-each_type_starttime)/60.0))
    print("爬取所有组图片共耗时:{:.2f}min".format((time.time()-all_starttime)/60.0))


        # break
        




    '''
    第一步， 获得所有类型的首页地址，共9个类型
    第二步， 在具体类型的首页中，获得套图的缩略图地址(也是套图的首页地址)，并且获得总页数
    第三步， 根据第二步获得的缩略图地址，找到第一张图片和总页数(即总张数)
    第四步， 解析第三步中图片的地址，并写入本地保存(使用对应的文件夹保存)
    '''
