from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import quote
import pymysql
import requests
from collections import OrderedDict
import time
import threading
# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')
# browser = webdriver.Chrome(chrome_options = chrome_options)

#超水代码
class connect_mysql():
    def __init__(self,db):
        import pymysql
        self.db = pymysql.connect(host='localhost', user='root', password='123456', port=3306, db=db)

    def inject_mysql(self,table,item):

        print(item)
        values = ','.join(['%s'] * len(item.values()))
        keys = ','.join(item.keys())
        cursor = self.db.cursor()

        try:
            sql = 'insert into %s (%s) values (%s)' % (table, keys, values)
            # print('sql:',sql)
            # print('tuple(item.values()):',tuple(item.values()))
            # sql = 'INSERT INTO %s (name,space_url,alter_fans,number,date,user_id) values(%s)' % (table, values)
            cursor.execute(sql, tuple(item.values()))
            self.db.commit()
            print('存储完成！')


        except Exception as e:
            print('存储失败')
            # print('错误为：')
            # print('str(e):\t\t', str(e))# 输出 str(e):		integer division or modulo by zero
            # print('repr(e):\t', repr(e))  # 输出 repr(e):	ZeroDivisionError('integer division or modulo by zero',)
            self.db.rollback()
    def close_db(self):
        print('关闭数据库')
        self.db.close()
    def get_mysqldata(self,sql):
        cursor = self.db.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        # print('results:',results)
        return results

        pass

class crawl_biliob():
    def __init__(self):
        self.start_url = 'https://www.biliob.com/rank/fans-increase/'
        self.db = 'b_project'
        self.table = 'biliob'
        self.base_url = 'https://space.bilibili.com/'
    def crawl(self):
        # try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        browser = webdriver.Chrome(chrome_options=chrome_options)
        # browser = webdriver.Chrome()
        wait = WebDriverWait(browser, 30)
        # if url.split('/')[-2] == 'fans-increase':
        browser.get(self.start_url)
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.container')))
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.v-card__text  a')))
        self.a_list = browser.find_elements_by_css_selector('.v-card__text  a')
        self.get_a_list_information(alter_fans=1)
        # elif url.split('/')[-2] == 'fans-decrease':

        button1 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.v-card__actions > button')))
        button1.click()
        button2 = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.v-slide-group__wrapper > div > div:nth-child(3)')))
        button2.click()

        #无语了
        time.sleep(2)
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.container')))
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.v-card__text  a')))
        self.a_list = browser.find_elements_by_css_selector('.v-card__text  a')
        self.get_a_list_information(alter_fans=0)
            # print(a_list[0].text.split('\n'))
        browser.close()
        # except:
        #     print('some errors happened')

    def get_a_list_information(self,alter_fans):

        for a in self.a_list:
            item = OrderedDict()
            result_list = a.text.split('\n')

            href = a.get_attribute('href')
            id = href.split('/')[-1]

            space_url = self.base_url + id

            #要按这个顺序！
            item['name'] = result_list[0]
            item['space_url'] = space_url
            item['alter_fans'] = alter_fans
            item['number'] = result_list[-1]
            item['date'] = time.strftime("%Y-%m-%d", time.localtime())
            item['user_id'] = int(id)

            mysql = connect_mysql(db=self.db)
            mysql.inject_mysql(self.table, item)

from urllib.parse import urlencode
class crawl_bilibili():
    def __init__(self,base_table,video_table):
        # self.base_urls = base_urls
        self.lock = threading.Lock()
        self.base_table = base_table
        self.video_table = video_table
        self.init_time = True
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36')
        chrome_options.add_argument('--headless')

        chrome_options.add_argument(
            '--proxy-server=http://proxy:orderId=O20091914563879906967&time=1600705092&sign=21e4e71bce73c337603c357a19eb8412&pid=0&cid=0&uid=&sip=0&nd=0@flow.hailiangip.com:14223')
        self.browser = webdriver.Chrome(options=chrome_options)
        pass
    def load_cookies(self):
        import json

        # 记得写完整的url 包括http和https
        self.browser.get('https://www.bilibili.com/')
        # self.browser.get('http://httpbin.org/get')
        # 首先清除由于浏览器打开已有的cookies
        self.browser.delete_all_cookies()

        with open('cookies.txt', 'r') as cookief:
            # 使用json读取cookies 注意读取的是文件 所以用load而不是loads
            cookieslist = json.load(cookief)

            # 方法1 将expiry类型变为int
            #     for cookie in cookieslist:
            #         #并不是所有cookie都含有expiry 所以要用dict的get方法来获取
            #         if isinstance(cookie.get('expiry'), float):
            #             cookie['expiry'] = int(cookie['expiry'])
            #         driver.add_cookie(cookie)
            # 方法2删除该字段
            for cookie in cookieslist:
                # 该字段有问题所以删除就可以  浏览器打开后记得刷新页面 有的网页注入cookie后仍需要刷新一下
                if 'expiry' in cookie:
                    del cookie['expiry']
                self.browser.add_cookie(cookie)
    def crawl(self,base_urls):
        self.base_urls = base_urls
        for base_url in self.base_urls:
            self.crawl_one(base_url)
    def crawl_one(self,base_url):
        if self.init_time == True:
            self.load_cookies()
            self.init_time = False


        wait = WebDriverWait(self.browser, 30)
        db_connect = connect_mysql(db='b_project')

        self.browser.get(base_url)

        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.main-content')))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.n-statistics')))
        ul = self.browser.find_element_by_css_selector('.be-pager')
        li_list = self.browser.find_elements_by_css_selector('.content > ul:nth-child(2) > li')
        #视频播放量

        video_num = self.browser.find_element_by_css_selector('.n-tab-links > a:nth-child(3) .n-num').text
        right_div = self.browser.find_element_by_css_selector('.n-statistics')
        print('列表为:',right_div.find_elements_by_css_selector('.n-data'))
        #关注数
        concerns_num = right_div.find_element_by_css_selector('a:nth-child(1) > #n-gz').text
        #粉丝数
        fans_num = right_div.find_element_by_css_selector('a:nth-child(2) > #n-fs').text

        #获赞数
        compliments_num = right_div.find_element_by_css_selector('.n-data:nth-child(3) > #n-bf').text


        #播放数
        play_num = right_div.find_element_by_css_selector('.n-data:nth-child(4) > #n-bf').text
        #阅读数

        read_num = right_div.find_element_by_css_selector('.n-data:nth-child(5) > #n-bf').text
        item_base = OrderedDict()
        user_id = base_url.split('/')[-2]
        item_base['user_id'] = user_id
        item_base['video_num'] = video_num
        item_base['concerns_num'] = concerns_num
        item_base['fans_num'] = fans_num
        item_base['compliments_num'] = compliments_num
        item_base['play_num'] = play_num
        item_base['read_num'] = read_num
        db_connect.inject_mysql(table=self.base_table, item=item_base)

        if ul.get_attribute('style') == 'display: none;':
            for li in li_list:

                item_video = OrderedDict()
                href = li.find_element_by_css_selector('.cover').get_attribute('href')
                time_ = li.find_element_by_css_selector('.time').text.rstrip()



                item_video['user_id'] = user_id
                item_video['video_url'] = href
                item_video['time'] = time_
                db_connect.inject_mysql(table=self.video_table, item=item_video)


        else:
            max_page_content = self.browser.find_element_by_css_selector('.be-pager-total').text

            import re
            pattern = '.*? ([0-9]*) .*?'
            max_page = re.match(pattern, max_page_content).group(1)
            time.sleep(1.5)
            for page in range(2,int(max_page)+1):
                params = {'tid': '0',
                          'page': page,
                          'keyword': '',
                          'order': 'pubdate'
                          }
                url = base_url + urlencode(params)
                print(url)
                self.browser.get(url)
                wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.main-content')))
                ul = self.browser.find_element_by_css_selector('.be-pager')
                li_list = self.browser.find_elements_by_css_selector('.content > ul:nth-child(2) > li')
                for li in li_list:
                    item_base = OrderedDict()
                    item_video = OrderedDict()
                    href = li.find_element_by_css_selector('.cover').get_attribute('href')
                    time_ = li.find_element_by_css_selector('.time').text.rstrip()

                    item_video['user_id'] = user_id
                    item_video['video_url'] = href
                    item_video['time'] = time_
                    db_connect.inject_mysql(table=self.video_table, item=item_video)
                time.sleep(1.5)


        time.sleep(1.5)
        # print('href:',href)
        # print('time:',time)
def spread_thread(urls,thread_num):

    urls_group = [[] for x in range(thread_num)]
    for i in range(len(urls)):
        urls_group[i%thread_num].append(urls[i])
    return urls_group


def main_1():
    b = crawl_biliob()
    b.crawl()


def main_2():
    start_time = time.time()

    base_table = 'bilibili_base_info'
    video_table = 'bilibili_video_info'
    table = 'biliob'

    #提取mysql数据
    # date = time.strftime("%Y-%m-%d", time.localtime())
    date = '2020-09-21'
    sql = 'select space_url from %s where date = "%s"'%(table,str(date))
    # sql = 'select space_url from %s where id BETWEEN 2 and 6'
    db_connect = connect_mysql(db='b_project')
    results = db_connect.get_mysqldata(sql)

    #加入待处理表中
    urls = []
    for r in results:
        url = r[0]+'/video?'
        print(url)
        urls.append(url)

    B = crawl_bilibili(video_table=video_table, base_table=base_table)

    # #使用多线程
    # thread_num = 20
    #
    # urls_group = spread_thread(urls,thread_num)
    # for i in range(thread_num):


    B.crawl(base_urls=urls)
    end_time = time.time()
    print('用时：',end_time - start_time)


if __name__ == '__main__':
    # main_1()
    # main_2()
    start_time = time.time()

    base_table = 'bilibili_base_info_test'
    video_table = 'bilibili_video_info_test'
    table = 'biliob'

    #提取mysql数据
    # date = time.strftime("%Y-%m-%d", time.localtime())
    date = '2020-09-21'
    sql = 'select space_url from %s where date = "%s"'%(table,str(date))
    # sql = 'select space_url from %s where id BETWEEN 2 and 6'
    db_connect = connect_mysql(db='b_project')
    results = db_connect.get_mysqldata(sql)

    #加入待处理表中
    urls = []
    for r in results:
        url = r[0]+'/video?'
        # print(url)
        urls.append(url)



    #使用多线程
    thread_num = 40

    urls_group = spread_thread(urls,thread_num)
    print(urls_group)
    t_list = []
    for i in range(thread_num):
        B = crawl_bilibili(video_table=video_table, base_table=base_table)
        t = threading.Thread(target=B.crawl,args=(urls_group[i],))
        print('线程%s设置完毕'%i)
        t_list.append(t)
    for t in t_list:
        t.setDaemon(True)
        t.start()
    for t in t_list:
        t.join()

    # B.crawl(base_urls=urls)
    end_time = time.time()
    print('用时：',end_time - start_time)