'''
前提条件：需要在文件工程下添加那个下面的js文件。

断断续续写了一周,
涉及功能：
request 获取网页代码
json & execjs   python调用js代码
os 文件的读写
re 正则表达式的应用

'''


import json
import time
import os
import re
import execjs
import requests

host= "https://img01.eshanyao.com" #'https://mhcdn.manhuazj.com/'
l_url = "https://www.manhuadui.com"
url = "https://www.manhuadui.com/manhua/jinjidejuren/"
headers = {  # 模拟浏览器访问网页
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'}
proxies={'http':'http://127.0.0.1:8888','https':'https://127.0.0.1:8888'}
response = requests.get(url=url)

artifacts_path = os.path.dirname(os.path.abspath('.')) + '/artifacts/'
artifacts_dir_path = 'juren/'

def main():
    #获取章节地址
    mkdirs() # 创建文件夹
    list_source = dir()
    list_source = list_source[len(list_source)-3:] #只爬取最新3话
    get_chapters(list_source)


'''
功能：查找所有章节网址
返回值：字符串：包含每个章节的url以及章节名称
'''
def dir():
    #正则，匹配章节url以及章节名称
    pattern = re.compile('href=\"\/manhua\/.+\.html.+title=.+\"')
    print("dir 正则过滤-----------------------------")
    print("正在查找该漫画所有章节的url以及名称")
    list_source=pattern.findall(response.text)
    print("章节所有url:",list_source)
    return list_source

def mkdirs():
    chapter_path = artifacts_path + artifacts_dir_path

    if not os.path.exists(artifacts_path):
        print ('创建%s主文件夹', artifacts_path)
        os.mkdir(artifacts_path)

    if not os.path.exists(chapter_path):
        print ('创建%s漫画文件夹', chapter_path)
        os.mkdir(chapter_path)


'''
功能：获得章节的url以及名称
心得：正则表达式的写法以及python正则表达式的使用
'''
def get_chapters(list_source):

    #遍历所有章节的url
    i=0
    for chapter in list_source:


        #print(chapter)
        r_url = re.search('\/manhua\/.+\.html', chapter).group()
        # 章节url
        chapter_url = l_url + r_url
        print(chapter_url)
        chapter_name = re.search('title=\".+\" ', chapter).group()
        chapter_name = chapter_name[7:-2]
        print(chapter_name)

        #获取具体章节网页的静态代码
        res = requests.get(chapter_url, headers)

        chapter_image_list = get_js_chapterImage(res)
        chapter_path = get_chapter_Path(res)

        print("down_url:")
        chapter_root=artifacts_dir_path+chapter_name # eg. juren/127话
        dir_path = artifacts_path + chapter_root

        # 判断如果本地已经有当前章节，则结束
        if os.path.exists(dir_path):
            print("已存在当前章节'%s'"%chapter_name)
            continue
        count=1
        for chapter_image in chapter_image_list:
            down_url = host+'/'+chapter_path+chapter_image
            print(down_url)
            download_image(down_url,chapter_root,chapter_image,count)
            count+=1

        # 降低服务器压力，每爬取一个章节的所有图片，延时10秒
        # 每爬取5个章节，再延时20秒
        print(chapter_name+'章节下载完毕，即将延时3秒爬取下一章节')
        time.sleep(3)
        i += 1
        # if (i % 5 == 0):
        #     print('延时60秒')
        #     time.sleep(5)

#这里从网页的script标签里，找数据,chapterImage被后台加密，放到script标签里
'''
参数：章节url
ex:https://www.manhuadui.com/manhua/guimiezhiren/410940.html
返回值：章节所有图片的名称 [***.jpg]
返回值类型：list
'''
def get_js_chapterImage(res):

    #print(res.text)
    #正则过滤数据
    chapter_image_code = re.search('chapterImages = \".+\";var chapterPath', res.text).group()
    chapter_image_code = re.search('\".+\"', chapter_image_code).group()
    print("chapter_image_code")
    print(chapter_image_code)
    chapter_image_code = chapter_image_code[1:-1]

    #解密章节图片乱码，还原成*.jpg格式
    chapter_Image_list = get_decryptImages(chapter_image_code)
    print("正在查询当前章节的所有图片")
    print(chapter_Image_list)

    return chapter_Image_list


def get_chapter_Path(res):
    chapter_path = re.search('chapterPath = \".+\";var chapterP', res.text).group()
    chapter_path = re.search('\".+\"', chapter_path).group()
    chapter_path = chapter_path[1:-1]
    #print(chapter_path)
    return chapter_path

def get_js():
    # f = open("D:/WorkSpace/MyWorkSpace/jsdemo/js/des_rsa.js",'r',encoding='UTF-8')
    f = open("decrypt20180904.js", 'r', encoding='UTF-8')
    line = f.readline()
    htmlstr = ''
    while line:
        htmlstr = htmlstr + line
        line = f.readline()
    #print(htmlstr)
    return htmlstr

#解密
def get_decryptImages(chapterImages):
    #获取解密js，进行解密
    js_str = get_js()
    ctx = execjs.compile(js_str)
    print(chapterImages)
    images =  ctx.call('decrypt20180904',chapterImages)

    #过滤数据：把字符串两边的符号["........."]过滤，以中间符号","进行切分
    images_list=str(images)[2:-2].split('","')

    return images_list


#下载图片
def download_image(url,chapter_root,image_name,count):

    root = artifacts_path+chapter_root+'/'

    #url = 'https://mhcdn.manhuazj.com/images/comic/5/8412/1551394269327841209ad0db6d.jpg'
    path = root + str(count)+'页.jpg'

    print(path)
    try:

        if not os.path.exists(root): # 判断根目录是否存在，os.madir()创建根目录
            print ('创建%s章节文件夹', root)
            os.mkdir(root)

        if not os.path.exists(path): # 判断文件是否存在，不存在将从get函数获取
            r = requests.get(url)

            with open(path, 'wb')as f:
                # wb存为二进制文件
                f.write(r.content)
                # 将返回内容写入文件 r.content返回二进制形式

                f.close()
                print('文件保存成功')
        else:
                print('文件已经存在')
    except:
        print('爬取失败')


if __name__ == '__main__':
    main()
