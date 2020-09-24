import requests
import urllib
import json as js
from lxml import etree
import datetime
import arrow
import pymysql
import b_project_data

fail_time = 0

class BilibiliVideo(object):
    def video_crawler_all(self,start_urls):
        for start_url in start_urls:
            self.video_crawler(start_url)
    def video_crawler(self,start_url):
        import re
        try:
            print('开始！')
            # proxypool_url = 'http://127.0.0.1:5555/random'
            # proxy = requests.get(proxypool_url).text.strip()
            # print('proxy:',proxy)
            # proxies = {'http': 'http://' + proxy}
            user_agents = ['Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)',
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2',
            'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:15.0) Gecko/20100101 Firefox/15.0.1',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',]
            import random
            user_agent = random.choice(user_agents)
            headers = {
                'User-Agent':user_agent,
                'Cookie': 'buvid3=675276DA-BB88-4AC3-A6CE-10404B33A0D485458infoc; rpdid=kxqllkomiwdospsmiwkxw; _uuid=6C3F48BC-1719-BF29-12B2-43CAFC8D39D363709infoc; LIVE_BUVID=AUTO6415865058656543; blackside_state=1; CURRENT_FNVAL=80; PVID=1; sid=8kvzigj6; finger=481832271; arrange=matrix; DedeUserID=20672743; DedeUserID__ckMd5=df944e71f5c786b2; SESSDATA=c990d87f%2C1616293630%2C51619*91; bili_jct=6cbf050203e93d8959260b5c16446eed'
            }
            print('判断代理是否成功：')
            # print(requests.get(url='http://httpbin.org/get', headers = headers).text)
            # print(requests.get(url='http://httpbin.org/get', proxies=proxies,headers = headers).text)

            requests.packages.urllib3.disable_warnings()
            import time
            time.sleep(1)
            homepage_text = requests.get(url=start_url, headers=headers, verify=False).text
            # homepage_text = requests.get(url=start_url, headers=headers, verify=False,proxies = proxies).text
            tree = etree.HTML(homepage_text)

            # 名称
            title = tree.xpath('//*[@id="viewbox_report"]/h1/@title')[0]
            print('title')

            # 简介
            intro = tree.xpath('//*[@id="v_desc"]/div[2]/text()')[0]
            intro = intro.replace(' ', '')
            intro = intro.replace('\n', '')
            print('intro')

            # tag
            tags = []
            taglist = tree.xpath('//*[@id="v_tag"]/ul/li')
            for i in taglist:
                tag = i.xpath('./div/a/span/text() | ./a/span/text() | ./div/a/text()')[0]
                tags.append(tag)
            tagraw = tags
            tags = []
            for i in tagraw:
                i = i.replace(' ', '')
                i = i.replace('\n', '')
                tags.append(i)
            print('tag')

            # 发视频时间
            start_time = tree.xpath('//*[@id="viewbox_report"]/div/span[3]/text()')[0]
            print('uptime')

            # bvid
            right = re.match(r'.*video/(.*)', start_url)
            bvid = right.group(1)

            # avid '414613105'
            av = tree.xpath('/html/head/meta[10]/@content')[0]
            mat = re.match(r'.*/av(.*)/', av)
            avid = mat.group(1)

            # oid/cid
            oidurl = 'https://api.bilibili.com/x/player/pagelist?'
            param = {
                'bvid': bvid,
                'jsonp': 'jsonp'
            }
            oid = requests.get(url=oidurl, params=param, headers=headers, verify=False).json()['data'][0]['cid']
            # oid = requests.get(url=oidurl, params=param, headers=headers, verify=False,proxies=proxies).json()['data'][0]['cid']

            # 各种数量
            raw_url = "http://api.bilibili.com/archive_stat/stat?aid=" + str(avid) + "&type=jsonp"
            response = urllib.request.urlopen(raw_url)
            raw_data = js.loads(response.read().decode("utf8"))['data']

            play_num = raw_data['view']
            danmaku = raw_data['danmaku']
            reply = raw_data['reply']
            favorite = raw_data['favorite']
            coin = raw_data['coin']
            share = raw_data['share']
            like = raw_data['like']
            print('intro number')

            # 视频可以选择的弹幕月份
            right = re.match('(.*)-(.*)-(.*) (.*)', start_time)
            year = int(right.group(1))
            month = int(right.group(2))
            day = int(right.group(3))

            now = now = datetime.datetime.now().strftime('%Y-%m')
            right = re.match('(.*)-(.*)', now)
            nowy = int(right.group(1))
            nowm = int(right.group(2))

            num = (nowy - year) * 12 + (nowm - month)

            bb = arrow.get(str(start_time), 'YYYY-MM-DD HH:mm:ss')

            allow_month = []
            for x in range(0, num + 1):
                allow_month.append(bb.shift(months=+x).format("YYYY-MM"))

            # 视频可以选择的弹幕时间
            requests.packages.urllib3.disable_warnings()
            timeurl = 'https://api.bilibili.com/x/v2/dm/history/index?'

            allow_days = []
            print(start_url)
            for i in allow_month:
                param = {
                    'type': 1, 'oid': oid, 'month': str(i)}

                timelist_base = requests.get(url=timeurl, params=param, headers=headers, verify=False).json()
                # timelist_base = requests.get(url=timeurl, params=param, headers=headers, verify=False,proxies = proxies).json()
                print('timelist_base:',timelist_base)
                # timelist = requests.get(url=timeurl, proxies = proxies,params=param, headers=headers, verify=False).json()['data']
                timelist = requests.get(url=timeurl, params=param, headers=headers, verify=False).json()['data']
                if timelist is None:
                    continue
                # print('allow_days:',allow_days)
                # print('timelist:',timelist)
                allow_days = allow_days + timelist
                time.sleep(0.5)
            print(allow_days)
            tm = {}
            for i in allow_days:
                tm[i] = []
                tanmuurl = 'https://api.bilibili.com/x/v2/dm/history?'

                param = {
                    'type': '1',
                    'oid': oid,
                    'date': str(i)
                }
                print('tanmuurl:',tanmuurl)
                response = requests.get(url=tanmuurl, params=param, headers=headers, verify=False)
                # response = requests.get(url=tanmuurl, params=param, headers=headers, verify=False,proxies = proxies)
                html = etree.HTML(response.content)
                result = html.xpath('//d')
                for j in range(0, len(result)):
                    tm[i].append(result[j].text)
            print('danma')

            # 爬评论
            replies = []
            times = []
            levels = []
            belikes = []
            page = 1
            replycount = 100
            while len(replies) < replycount:
                replyurl = 'https://api.bilibili.com/x/v2/reply?pn=' + str(page) + '&type=1&oid=' + avid
                reply_response = requests.get(url=replyurl, headers=headers, verify=False).json()
                # reply_response = requests.get(url=replyurl, headers=headers, verify=False,proxies = proxies).json()
                print('reply_url:',replyurl)
                print('reply_response:',reply_response)
                replylist = reply_response['data']['replies']
                replycount = int(reply_response['data']['page']['count'])
                for i in replylist:
                    re = i['content']['message']
                    time = i['ctime']
                    level = i['member']['level_info']['current_level']
                    belike = i['like']
                    replies.append(re)
                    times.append(time)
                    levels.append(level)
                    belikes.append(belike)
                page += 1
            print('reply')

            print('connect mysql')

            connection = pymysql.connect(host='localhost',
                                         user='root',
                                         password='123456',
                                         db='b_project',
                                         )
            cur = connection.cursor()

            infosql = 'insert into vinfo values(' + "'" + start_url + "'" + ',' + "'" + title + "'" + ',' + "'" + intro + "'" + ',' + "'" + start_time + "'" + ',' + "'" + str(
                play_num) + "'" + ',' + "'" + str(danmaku) + "'" + ',' + "'" + str(reply) + "'" + ',' + "'" + str(
                replycount) + "'" + ',' + "'" + str(favorite) + "'" + ',' + "'" + str(coin) + "'" + ',' + "'" + str(
                share) + "'" + ',' + "'" + str(like) + "'" + ')'
            try:
                cur.execute(infosql)
                print('vinfo 载入成功')
            except:
                print('存储失败')

            for i in tm:
                for j in tm[i]:
                    j = j.replace(' ', '')
                    j = j.replace('\n', '')
                    j = j.replace("'","")
                    j = j.replace("\\","")

                    print('i:',i)
                    print('j:',j)
                    danmasql = 'insert into danmaku values(' + "'" + start_url + "'" + ',' + "'" + i + "'" + ',' + "'" + j + "'" + ')'
                    try:
                        cur.execute(danmasql)
                    except:
                        print('存储失败')

            print('danmaku载入成功')
            for i in range(0, len(replies)):
                x = replies[i]
                x = x.replace(' ', '')
                x = x.replace('\n', '')
                x = x.replace('\\','')
                c = times[i]
                l = levels[i]
                b = belikes[i]
                resql = 'insert into reply values(' + "'" + start_url + "'" + ',' + "'" + str(x) + "'" + ',' + "'" + str(
                    c) + "'" + ',' + "'" + str(l) + "'" + ',' + "'" + str(b) + "'"')'
                try:
                    cur.execute(resql)
                except:
                    print('存储失败')
            print('reply载入成功')
        except Exception as e:
            print(str(e))
            print('读取失败')
            global fail_time
            fail_time += 1
            return
        connection.commit()
        cur.close()
        # 关闭数据库连接
        connection.close()
        b = b_project_data.connect_mysql(db='b_project')
        table = 'bilibili_video_info'
        sql = "update %s set flag = 1"%table
        cursor = b.db.cursor()
        cursor.execute(sql)
        b.close_db()
        return

def spread_thread(urls,thread_num):
    urls_group = [[] for x in range(thread_num)]
    for i in range(len(urls)):
        urls_group[i%thread_num].append(urls[i])
    return urls_group

if __name__ == '__main__':
    import time
    import threading
    start_time = time.time()
    c = b_project_data.connect_mysql(db = 'b_project')
    sql = 'SELECT video_url FROM bilibili_video_info where  flag = 0'
    raw_urls = c.get_mysqldata(sql)
    urls = []
    for url in raw_urls:
        urls.append(url[0])
    print('urls:',urls)
    #
    # thread_num = 5
    # urls_group = spread_thread(urls,thread_num)
    # print(urls_group)
    # t_list = []
    # for i in range(thread_num):
    #     B = BilibiliVideo()
    #     t = threading.Thread(target=B.video_crawler_all,args=(urls_group[i],))
    #     print('线程%s设置完毕'%i)
    #     t_list.append(t)
    # for t in t_list:
    #     t.setDaemon(True)
    #     t.start()
    #     print('线程开启！')
    #
    #     time.sleep(2)
    # for t in t_list:
    #     t.join()
    B= BilibiliVideo()
    B.video_crawler(start_url = 'https://www.bilibili.com/video/BV1ex411X71S')
    end_time = time.time()

    print('用时：',end_time-start_time)
    # print('总请求次数:',len(urls))
    # print('失败次数:',fail_time)
    # print('成功率:',1-fail_time/len(urls))

# video_crawler(start_url = 'https://www.bilibili.com/video/BV14V411m7hd')

